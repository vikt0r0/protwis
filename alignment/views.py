﻿from django.shortcuts import render
from django.conf import settings
from django.views.generic import TemplateView
from django.db.models import Case, When

from common.views import AbsTargetSelection
from common.views import AbsSegmentSelection
from common.views import AbsMiscSelection
from structure.functions import BlastSearch

# from common.alignment_SITE_NAME import Alignment
Alignment = getattr(__import__('common.alignment_' + settings.SITE_NAME, fromlist=['Alignment']), 'Alignment')
from protein.models import Protein, ProteinSegment,ProteinFamily, ProteinSet
from residue.models import ResiduePositionSet

import inspect, os
from collections import OrderedDict

from common import definitions

class TargetSelection(AbsTargetSelection):
    step = 1
    number_of_steps = 2
    docs = 'sequences.html#structure-based-alignments'
    selection_boxes = OrderedDict([
        ('reference', False),
        ('targets', True),
        ('segments', False),
    ])
    buttons = {
        'continue': {
            'label': 'Continue to next step',
            'url': '/alignment/segmentselection',
            'color': 'success',
        },
    }

class TargetSelectionGprotein(AbsTargetSelection):
    step = 1
    number_of_steps = 2
    psets = False
    filters = True
    filter_gprotein = True

    docs = 'sequences.html#structure-based-alignments'

    selection_boxes = OrderedDict([
        ('reference', False),
        ('targets', True),
        ('segments', False),
    ])
    buttons = {
        'continue': {
            'label': 'Continue to next step',
            'url': '/alignment/segmentselectiongprot',
            'color': 'success',
        },
    }
    try:
        ppf = ProteinFamily.objects.get(slug="100_000")
        pfs = ProteinFamily.objects.filter(parent=ppf.id)
        ps = Protein.objects.filter(family=ppf)
        tree_indent_level = []
        action = 'expand'
        # remove the parent family (for all other families than the root of the tree, the parent should be shown)
        del ppf
    except Exception as e:
        pass

class SegmentSelection(AbsSegmentSelection):
    step = 2
    number_of_steps = 2
    docs = 'sequences.html#structure-based-alignments'
    selection_boxes = OrderedDict([
        ('reference', False),
        ('targets', True),
        ('segments', True),
    ])
    buttons = {
        'continue': {
            'label': 'Show alignment',
            'url': '/alignment/render',
            'color': 'success',
        },
    }

class SegmentSelectionGprotein(AbsSegmentSelection):
    step = 2
    number_of_steps = 2
    docs = 'sequences.html#structure-based-alignments'
    description = 'Select sequence segments in the middle column for G proteins. You can expand every structural element and select individual' \
        + ' residues by clicking on the down arrows next to each helix, sheet or loop.\n\n You can select the full sequence or show all structured regions at the same time.\n\nSelected segments will appear in the' \
        + ' right column, where you can edit the list.\n\nOnce you have selected all your segments, click the green' \
        + ' button.'
    
    template_name = 'common/segmentselection.html'

    selection_boxes = OrderedDict([
        ('reference', False),
        ('targets', True),
        ('segments', True),
    ])
    buttons = {
        'continue': {
            'label': 'Show alignment',
            'url': '/alignment/render',
            'color': 'success',
        },
    }

    position_type = 'gprotein'
    rsets = ResiduePositionSet.objects.filter(name__in=['Gprotein Barcode', 'YM binding site']).prefetch_related('residue_position')

    ss = ProteinSegment.objects.filter(name__regex = r'^[a-zA-Z0-9]{1,5}$', partial=False).prefetch_related('generic_numbers')
    ss_cats = ss.values_list('category').order_by('category').distinct('category')


class BlastSearchInput(AbsMiscSelection):
    step = 1
    number_of_steps = 1
    docs = 'sequences.html#similarity-search-blast'
    title = 'BLAST search'
    description = 'Enter a sequence into the text box and press the green button.'
    buttons = {
        'continue': {
            'label': 'BLAST',
            'onclick': 'document.getElementById("form").submit()',
            'color': 'success',
        },
    }
    selection_boxes = {}
    blast_input = True


class BlastSearchResults(TemplateView):
    """
    An interface for blast similarity search of the input sequence.
    """
    template_name="blast/blast_search_results.html"

    def post(self, request, *args, **kwargs):

        if 'human' in request.POST.keys():
            blast = BlastSearch(blastdb=os.sep.join([settings.STATICFILES_DIRS[0], 'blast', 'protwis_human_blastdb']), top_results=50)
            blast_out = blast.run(request.POST['input_seq'])
        else:
            blast = BlastSearch(top_results=50)
            blast_out = blast.run(request.POST['input_seq'])

        context = {}
        context['results'] = [(Protein.objects.get(pk=x[0]), x[1]) for x in blast_out]
        context["input"] = request.POST['input_seq']

        return render(request, self.template_name, context)


def render_alignment(request):
    # get the user selection from session
    simple_selection = request.session.get('selection', False)
    
    # create an alignment object
    a = Alignment()

    # load data from selection into the alignment
    a.load_proteins_from_selection(simple_selection)
    a.load_segments_from_selection(simple_selection)

    # build the alignment data matrix
    check = a.build_alignment()
    if check == 'Too large':
        return render(request, 'alignment/error.html', {'proteins': len(a.proteins), 'residues':a.number_of_residues_total})
    # calculate consensus sequence + amino acid and feature frequency
    a.calculate_statistics()

    num_of_sequences = len(a.proteins)
    num_residue_columns = len(a.positions) + len(a.segments)

    return render(request, 'alignment/alignment.html', {'a': a, 'num_of_sequences': num_of_sequences,
        'num_residue_columns': num_residue_columns})

def render_family_alignment(request, slug):
    # create an alignment object
    a = Alignment()

    # fetch proteins and segments
    proteins = Protein.objects.filter(family__slug__startswith=slug, sequence_type__slug='wt')

    if slug.startswith('100'):

        gsegments = definitions.G_PROTEIN_SEGMENTS

        preserved = Case(*[When(slug=pk, then=pos) for pos, pk in enumerate(gsegments['Full'])])
        segments = ProteinSegment.objects.filter(slug__in = gsegments['Full'], partial=False).order_by(preserved)
    else:
        segments = ProteinSegment.objects.filter(name__regex = r'.{5}.*', partial=False)

    # load data into the alignment
    a.load_proteins(proteins)
    a.load_segments(segments)

    # build the alignment data matrix
    a.build_alignment()

    # calculate consensus sequence + amino acid and feature frequency
    a.calculate_statistics()

    num_of_sequences = len(a.proteins)
    num_residue_columns = len(a.positions) + len(a.segments)

    return render(request, 'alignment/alignment.html', {'a': a, 'num_of_sequences': num_of_sequences,
        'num_residue_columns': num_residue_columns})

def render_fasta_alignment(request):
    # get the user selection from session
    simple_selection = request.session.get('selection', False)
    
    # create an alignment object
    a = Alignment()
    a.show_padding = False

    # load data from selection into the alignment
    a.load_proteins_from_selection(simple_selection)
    a.load_segments_from_selection(simple_selection)

    # build the alignment data matrix
    a.build_alignment()
    
    response = render(request, 'alignment/alignment_fasta.html', context={'a': a}, content_type='text/fasta')
    response['Content-Disposition'] = "attachment; filename=" + settings.SITE_TITLE + "_alignment.fasta"
    return response

def render_fasta_family_alignment(request, slug):
    # create an alignment object
    a = Alignment()
    a.show_padding = False

    # fetch proteins and segments
    proteins = Protein.objects.filter(family__slug__startswith=slug, sequence_type__slug='wt')
    segments = ProteinSegment.objects.filter(partial=False)
    
    # load data into the alignment
    a.load_proteins(proteins)
    a.load_segments(segments)
    
    # build the alignment data matrix
    a.build_alignment()
    
    response = render(request, 'alignment/alignment_fasta.html', context={'a': a}, content_type='text/fasta')
    response['Content-Disposition'] = "attachment; filename=" + settings.SITE_TITLE + "_alignment.fasta"
    return response


def render_csv_alignment(request):
    # get the user selection from session
    simple_selection = request.session.get('selection', False)
    
    # create an alignment object
    a = Alignment()
    a.show_padding = False

    # load data from selection into the alignment
    a.load_proteins_from_selection(simple_selection)
    a.load_segments_from_selection(simple_selection)

    # build the alignment data matrix
    a.build_alignment()

    # calculate consensus sequence + amino acid and feature frequency
    a.calculate_statistics()
    
    response = render(request, 'alignment/alignment_csv.html', context={'a': a}, content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=" + settings.SITE_TITLE + "_alignment.csv"
    return response
