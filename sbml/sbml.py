import libsbml


def build_sbml(database_extractor, path, name):

    document = libsbml.SBMLDocument(3, 2)
    model = document.createModel()
    model.setId(name + "_" + database_extractor.database_name())
    model.setName(name)

    compartments(database_extractor, model)
    species(database_extractor, model)
    reactions(database_extractor, model)

    write_sbml(database_extractor, document, name, path)


def write_sbml(database_extractor, document, name, path):
    filename = path + '/' + name + '_' + database_extractor.database_name() + '.xml'
    libsbml.writeSBMLToFile(document, filename)


def reactions(database_extractor, model):
    for r in database_extractor.reactions.keys():
        reaction = database_extractor.reactions[r]
        sbml_reaction = model.createReaction()
        sbml_reaction.setId(reaction.__getitem__('ID'))
        sbml_reaction.setName(reaction.__getitem__('NAME')[0])
        for substrate in reaction.__getitem__('SUBSTRATES'):
            species_ref = model.createReactant()
            species_ref.setSpecies(substrate)
            species_ref.setStoichiometry(reaction.__getitem__('STOICHIOMETRY')[substrate])
        for product in reaction.__getitem__('PRODUCTS'):
            species_ref = model.createProduct()
            species_ref.setSpecies(product)
            species_ref.setStoichiometry(reaction.__getitem__('STOICHIOMETRY')[product])
        sbml_reaction.setReversible(reaction.__getitem__('REVERSIBLE'))
        sbml_reaction.setNotes(reaction_notes_string(reaction))

    print()


def species(database_extractor, model):
    for m in database_extractor.metabolites.keys():
        metabolite = database_extractor.metabolites[m]
        sbml_species = model.createSpecies()
        sbml_species.setId(metabolite.__getitem__('ID'))
        sbml_species.setName(metabolite.__getitem__('NAME')[0])
        sbml_species.setCompartment(metabolite.__getitem__('COMPARTMENT'))
        sbml_species.setNotes(metabolite_notes_string(metabolite))


def compartments(database_extractor, model):
    c = []
    for m in database_extractor.metabolites.keys():
        c.append(database_extractor.metabolites[m].__getitem__('COMPARTMENT'))
    c = set(c)
    for compartment in c:
        c = model.createCompartment()
        c.setId(compartment)
        c.setName(compartment)


def metabolite_notes_string(metabolite):
    notes_string = '<body xmlns="http://www.w3.org/1999/xhtml">\n'
    if not metabolite.__getitem__('CHARGE') == 'NA':
        notes_string += '\t<p>CHARGE: %s</p>\n' % metabolite.__getitem__('CHARGE')
    if not metabolite.__getitem__('FORMULA') == 'NA':
        notes_string += '\t<p>FORMULA: %s</p>\n' % metabolite.__getitem__('FORMULA')
    if not metabolite.__getitem__('INCHI') == 'NA':
        notes_string += '\t<p>INCHI: %s</p>\n' % metabolite.__getitem__('INCHI')
    if not metabolite.__getitem__('SMILES') == 'NA':
        notes_string += '\t<p>SMILES: %s</p>\n' % metabolite.__getitem__('SMILES')
    for db in metabolite.__getitem__('DB_LINKS').keys():
        notes_string += '\t<p>%s: %s</p>\n' % (db, metabolite.__getitem__('DB_LINKS')[db])
    notes_string += '</body>'
    return str(notes_string)


def reaction_notes_string(reaction):
    notes_string = '<body xmlns="http://www.w3.org/1999/xhtml">\n'
    notes_string += '\t<p>ENZYME: %s</p>\n' % ', '.join(reaction.__getitem__('ENZYME'))
    notes_string += '\t<p>PATHWAY: %s</p>\n' % ', '.join(reaction.__getitem__('PATHWAY'))
    notes_string += '\t<p>GENE_ASSOCIATION: %s</p>\n' % ', '.join(reaction.__getitem__('GENE_ASSOCIATION'))
    for db in reaction.__getitem__('DB_LINKS').keys():
        notes_string += '\t<p>%s: %s</p>\n' % (db, reaction.__getitem__('DB_LINKS')[db])
    notes_string += '</body>'
    return str(notes_string)
