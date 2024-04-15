from model import ClinicalTrial, Condition, Topic as DjangoTopic, Rating as DjangoRating, ConditionAnnotation, Gene as DjangoGene, GeneLabel, GeneAnnotation, GeneLink as GeneLinkDjango, Intervention, EntityLink as EntityLinkDjango, Entity, DrugLink as DrugLinkDjango, Drug as DjangoDrug, DrugName, DrugGeneLinkDetails
import owlready2 as owl
from tqdm import tqdm

#the url for ontology eventually will be normalized with the purl IRI

def create_empty_ontology() -> owl.Ontology:
    return owl.get_ontology("http://temporary.org/IRclinicaltrials.owl")
def create_graph():
    ontology = create_empty_ontology()
    with ontology:
        ### entities
        class ClinicalTrialDocument(owl.Thing):
            pass
        class ClinicalTrialDocumentPart(owl.Thing):
            pass
        class ConditionDisease(ClinicalTrialDocumentPart):
            pass
        class InterventionTreatment(ClinicalTrialDocumentPart):
            pass
        class Gene(owl.Thing):
            pass
        class Drug(owl.Thing):
            pass
        class Topic(owl.Thing):
            pass
        class Rating(owl.Thing):
            pass
        class CrossReferenceEntity(owl.Thing):
            pass
        class InterventionType(owl.Thing):
            pass
        class StudyType(owl.Thing):
            pass
        class Informational(StudyType):
            label = 'Informational'
        class Observational(StudyType):
            label = 'Observational'
        class ExpandedAccess(StudyType):
            label = 'Expanded Access'
        class PatientRegistry(Observational):
            label = 'Observational [Patient Registry]'
        class DrugIntervention(InterventionType):
            pass
        class Procedure(InterventionType):
            pass
        class Biological(InterventionType):
            pass
        class Other(InterventionType):
            pass
        class Behavioral(InterventionType):
            pass
        class Genetic(InterventionType):
            pass
        class Radiation(InterventionType):
            pass
        class Device(InterventionType):
            pass
        class DietarySupplement(InterventionType):
            pass
        class CombinationProduct(InterventionType):
            pass
        class DiagnosticTest(InterventionType):
            pass
        ### data properties
        class ClinicalTrialDocumentPartProperty(owl.DataProperty):
            pass
        class BriefTitle(ClinicalTrialDocumentPartProperty):
            pass
        class OfficialTitle(ClinicalTrialDocumentPartProperty):
            pass
        class NCTID(ClinicalTrialDocumentPartProperty):
            pass
        class Summary(ClinicalTrialDocumentPartProperty):
            pass
        class Description(ClinicalTrialDocumentPartProperty):
            pass
        class Criteria(ClinicalTrialDocumentPartProperty):
            pass
        class hasText(owl.DataProperty):
            pass
        class minimumAge(owl.DataProperty):
            pass
        class maximumAge(owl.DataProperty):
            pass
        class gender(owl.DataProperty):
            pass
        class hasText(owl.DataProperty):
            pass
        class crossReferenceURI(owl.DataProperty):
            pass
        class TopicProperty(owl.DataProperty):
            pass
        class TopicYear(TopicProperty):
            pass
        class TopicNumber(TopicProperty):
            pass
        class TopicDemography(TopicProperty):
            pass
        class TopicDisease(TopicProperty):
            pass

        class Other(TopicProperty):
            pass
        ### object properties

        class hasType(owl.ObjectProperty):
            domain = [InterventionTreatment]
            range = [InterventionType]

        class hasPart(owl.ObjectProperty):
            domain = [ClinicalTrialDocument]
            range = [ClinicalTrialDocumentPart]
        # ClinicalTrialDocument.equivalent_to = [hasPart.exactly(1,OfficialTitle), hasPart.exactly(1,BriefTitle), hasPart.exactly(1,Summary), hasPart.exactly(1,Description), hasPart.exactly(1,Criteria)]
        class hasStudyTypeAssignment(owl.ObjectProperty):
            domain = [ClinicalTrialDocument]
            range = [StudyType]
        class TopicGene(owl.ObjectProperty):
            pass
        class EntityLink(owl.ObjectProperty):
            domain = [ClinicalTrialDocument, ClinicalTrialDocumentPart, Topic]
            range = [CrossReferenceEntity]
        class DrugLink(owl.ObjectProperty):
            domain = [ClinicalTrialDocument, ClinicalTrialDocumentPart]
            range = [CrossReferenceEntity]
        class GeneLink(owl.ObjectProperty):
            domain = [ClinicalTrialDocument, ClinicalTrialDocumentPart]
            range = [CrossReferenceEntity]
        class targetsGene(owl.ObjectProperty):
            pass

        ### annotation properties

        class TradeName(owl.AnnotationProperty):
            pass
        class ChemicalName(owl.AnnotationProperty):
            pass
        class GenericName(owl.AnnotationProperty):
            pass
        class ScientificName(owl.AnnotationProperty):
            pass


        ### synthetic punning with singleton instances
        #intervention types
        procedure_it = Procedure()
        drug_it = DrugIntervention()
        biological_it = Biological()
        other_it = Other()
        behavioral_it = Behavioral()
        radiation_it = Radiation()
        genetic_it = Genetic()
        device_it = Device()
        diet_it = DietarySupplement()
        comb_it = CombinationProduct()
        test_it = DiagnosticTest()

        #study types
        informational_st = Informational()
        observational_st = Observational()
        ea_st = ExpandedAccess()
        patient_st = PatientRegistry()

        #relational objects
        drugs = DjangoDrug.objects.all()
        topics = DjangoTopic.objects.all()
        genes = DjangoGene.objects.all()
        ratings = DjangoRating.objects.all()
        all_trials = ClinicalTrial.objects.all()
        entities = Entity.objects.all()
        #dynamically created A-Box (entities have to be loaded first)
        #cross references (diseases) 
        for i, entity in tqdm(enumerate(entities)):
            url = entity.url.replace('#','')
            cross_entity = CrossReferenceEntity(url)
            cross_entity.label = entity.label
            cross_entity.crossReferenceURI = [url]
            cross_entity.hasText = [entity.label]
        #dynamically created T-Box
        #genes
        for i,gene in enumerate(genes):
            label = 'gene_' + gene.main_label.replace(' ','')
            gene_class = owl.types.new_class(label, (Gene, ))
            gene_class.label = gene.main_label
            gene_class.hasExactSynonym = [synonym.text for synonym in GeneLabel.objects.filter(gene = gene)]
        for gene in genes:
            label = 'gene_' + gene.main_label.replace(' ','')
            gene_class = ontology[label]
            if gene.family:
                superlabel = 'gene_' + gene.family.main_label.replace(' ','')
                superclass = ontology[superlabel]
                gene_class.is_a = [superclass]
        #drugs
        for i,drug in enumerate(drugs):
            trade_names = []
            generic_names = []
            chemical_names = []
            scientific_names = []
            for drugName in DrugName.objects.filter(drug = drug):
                
                if drugName.type == 'T':
                    trade_names.append(drugName.name)
                if drugName.type == 'G':
                    generic_names.append(drugName.name)
                if drugName.type == 'C':
                    chemical_names.append(drugName.name)
                if drugName.type == 'S':
                    scientific_names.append(drugName.name)
            label = 'drug_' + str(drug).replace(' ','')
            drug_class = owl.types.new_class(label, (Drug, ))
            drug_class.GenericName = generic_names
            drug_class.TradeName = trade_names
            drug_class.ChemicalName = chemical_names
            drug_class.ScientificName = scientific_names
            drug_class.label = str(drug)

            drug_class.targetsGene = [ontology['gene_'+gene_link.gene.main_label.replace(' ','')] for gene_link in DrugGeneLinkDetails.objects.filter(drug = drug)]
            # print([ontology['gene_'+gene.main_label.replace(' ','')] for gene in drug.genes.all()])
        ### dynamically created A-Box
        #topics
        for i, topic in tqdm(enumerate(topics)):
            iri = str(topic.year) + '_' + str(topic.topic_no)
            topic_entity = Topic(iri)
            topic_entity.TopicDemography = [topic.demo]
            topic_entity.TopicNumber = [topic.topic_no]
            topic_entity.TopicYear = [topic.year]
            topic_entity.TopicDisease = [topic.disease]
            genes = DjangoGene.objects.filter(pk__in = topic.genes_mtm.all())
            topic_entity.TopicGene = [ontology['gene_'+gene.main_label.replace(' ','')] for gene in genes]
            url = topic.disease_fl.url.replace('#','')
            topic_entity.EntityLink = ontology.search(iri = f'http://temporary.org/IRclinicaltrials.owl#{url}')

 
        #clinical trials
        found_single_drug_link = False
        found_single_gene_link = False
        for i, trial in tqdm(enumerate(all_trials)):
            #data properties
            document = ClinicalTrialDocument(trial.nctid)
            document.label = trial.nctid
            document.BriefTitle = [trial.brief_title]
            document.OfficialTitle = [trial.official_title]
            document.Summary = [trial.summary]
            document.Description = [trial.description]
            document.Criteria = [trial.criteria]
            document.minimumAge = [trial.min_age]
            document.maximumAge = [trial.max_age]
            document.gender = [trial.gender]
            #object properties
            #study type
            if trial.study_type == 'Informational':
                document.hasStudyTypeAssignment = [informational_st]
            elif trial.study_type == 'Observational':
                document.hasStudyTypeAssignment = [observational_st]
            elif trial.study_type == 'Expanded Access':
                document.hasStudyTypeAssignment = [ea_st]
            elif trial.study_type == 'Observational [Patient Registry]':
                document.hasStudyTypeAssignment = [patient_st]
            else:
                document.hasStudyTypeAssignment = [informational_st]

            #interventions
            interventions = Intervention.objects.filter(document = trial)
            intervention_list = []
            for j,intervention in enumerate(interventions) :
                intervention_entity = InterventionTreatment()
                if intervention.type == 'Procedure':
                    intervention_entity.hasType = [procedure_it]
                elif intervention.type == 'Drug':
                    intervention_entity.hasType = [drug_it]
                elif intervention.type == 'Biological':
                    intervention_entity.hasType = [biological_it]
                elif intervention.type == 'Other':
                    intervention_entity.hasType = [other_it]
                elif intervention.type == 'Behavioral':
                    intervention_entity.hasType = [behavioral_it]
                elif intervention.type == 'Radiation':
                    intervention_entity.hasType = [radiation_it]
                elif intervention.type == 'Genetic':
                    intervention_entity.hasType = [genetic_it]
                elif intervention.type == 'Device':
                    intervention_entity.hasType = [device_it]
                elif intervention.type == 'Dietary Supplement':
                    intervention_entity.hasType = [diet_it]
                elif intervention.type == 'Diagnostic Test':
                    intervention_entity.hasType = [test_it]
                elif intervention.type == 'Combination Product':
                    intervention_entity.hasType = [comb_it]
                else:
                    print(intervention.type)
                intervention_entity.hasText = [intervention.name]
                intervention_entity.label = trial.nctid + 'INT' + str(j)
                intervention_list.append(intervention_entity)
            #diseases
            conditions = Condition.objects.filter(document = trial)
            condition_list = []
            for j,condition in enumerate(conditions):
                condition_entity = ConditionDisease()
                condition_entity.label = trial.nctid + 'COND' + str(j)
                condition_entity.hasText = [condition.text]
                condition_list.append(condition_entity)
                entity_links = EntityLinkDjango.objects.filter(condition=condition)
                gene_links = GeneLinkDjango.objects.filter(condition=condition)
                drug_links = DrugLinkDjango.objects.filter(condition=condition)
                for link in entity_links:
                    url = link.entity.url.replace('#','')
                    entity = ontology.search(iri = f'http://temporary.org/IRclinicaltrials.owl#{url}')[0]
                    condition_entity.EntityLink.append(entity)
                for link in gene_links:
                    gene = ontology['gene_' + link.gene.main_label.replace(' ','')]
                    condition_entity.GeneLink.append(gene)
                for link in drug_links:
                    drug = ontology['drug_' + str(link.drug).replace(' ','')]
                    condition_entity.GeneLink.append(drug)
            #direct entity links
            entity_links = EntityLinkDjango.objects.filter(document=trial)
            gene_links = GeneLinkDjango.objects.filter(document=trial)
            drug_links = DrugLinkDjango.objects.filter(document=trial)
            for link in entity_links:
                url = link.entity.url.replace('#','')
                entity = ontology.search(iri = f'http://temporary.org/IRclinicaltrials.owl#{url}')[0]
                document.EntityLink.append(entity)
            for link in gene_links:
                found_single_gene_link = True
                gene = ontology['gene_' + link.gene.main_label.replace(' ','')]

                document.GeneLink.append(gene)
            for link in drug_links:
                found_single_drug_link = True
                drug = ontology['drug_' + str(link.drug).replace(' ','')]

                document.DrugLink.append(drug)
            document.hasPart = intervention_list + condition_list
            # if found_single_gene_link and found_single_drug_link:
            #     break
        class DiseaseScore(owl.DataProperty): pass
        class GeneScore(owl.DataProperty): pass
        class TreatmentScore(owl.DataProperty): pass
        class DemographyScore(owl.DataProperty): pass
        class TRECGeneAnnotation(owl.DataProperty): pass
        class TRECDiseaseAnnotation(owl.DataProperty): pass
        class TRECDemographyAnnotation(owl.DataProperty): pass
        class TRECPMAnnotation(owl.DataProperty): pass
        class TopicConnection(owl.ObjectProperty): pass
        class DocumentConnection(owl.ObjectProperty): pass
        for i, rating in tqdm(enumerate(ratings)):
            rating_entity = Rating('RAT_'+str(rating.topic.year)+'_'+str(rating.topic.topic_no)+'_'+rating.document.nctid)

            topic_iri = str(rating.topic.year) + '_' + str(rating.topic.topic_no)
            document_iri = rating.document.nctid
            rating_entity.TopicConnection = [ontology[topic_iri]]
            rating_entity.DocumentConnection = [ontology[document_iri]]

            rating_entity.DiseaseScore = [rating.disease_score]
            rating_entity.GeneScore = [rating.gene_score]
            rating_entity.TreatmentScore = [rating.treatment_score]
            rating_entity.DemographyScore = [rating.demography_score]

            rating_entity.TRECGeneAnnotation = [rating.pm_gene1_annotation_desc,rating.pm_gene2_annotation_desc,rating.pm_gene3_annotation_desc]
            rating_entity.TRECDiseaseAnnotation = [rating.pm_disease_desc]
            rating_entity.TRECDemographyAnnotation = [rating.pm_demo_desc]
            rating_entity.TRECPMAnnotation = [rating.pm_rel_desc]

            
    ontology.save('clinicalTrialsForIR.owl')

    