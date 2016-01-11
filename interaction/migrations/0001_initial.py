# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-11 13:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ligand', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProteinLigandInteraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'interaction_protein_ligand',
            },
        ),
        migrations.CreateModel(
            name='ResidueFragmentAtom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atomtype', models.CharField(max_length=20)),
                ('atomnr', models.SmallIntegerField()),
                ('atomclass', models.CharField(max_length=20)),
                ('residuename', models.CharField(max_length=20)),
                ('chain', models.CharField(max_length=20)),
                ('residuenr', models.SmallIntegerField()),
                ('x', models.DecimalField(decimal_places=3, max_digits=6)),
                ('y', models.DecimalField(decimal_places=3, max_digits=6)),
                ('z', models.DecimalField(decimal_places=3, max_digits=6)),
                ('occupancy', models.DecimalField(decimal_places=2, max_digits=6)),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=6)),
                ('element_name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'interaction_residue_fragment_atoms',
            },
        ),
        migrations.CreateModel(
            name='ResidueFragmentInteraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'interaction_residue_fragment',
            },
        ),
        migrations.CreateModel(
            name='ResidueFragmentInteractionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=50, null=True)),
                ('direction', models.CharField(max_length=30, null=True)),
            ],
            options={
                'db_table': 'interaction_type_residue_fragment',
            },
        ),
        migrations.CreateModel(
            name='StructureLigandInteraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdb_reference', models.CharField(max_length=3, null=True)),
                ('annotated', models.BooleanField(default=False)),
                ('ligand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ligand.Ligand')),
                ('ligand_role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ligand.LigandRole')),
            ],
            options={
                'db_table': 'interaction_structure_ligand',
            },
        ),
    ]
