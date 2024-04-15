from django.db import models


class ClinicalTrial(models.Model):
    """
    This class represents a singular clinical trial. It contains most of the document description.

    Fields:
    -----------
        nctid - primary key, char field

        brief_title - title of a document - char field, cannot be empty

        official_title - second title of a document - char field, cannot be empty

        desctription - detailed description of a document - char field, max length 4000

        summary - short summary of a document - char field, max length 4000

        criteria - eligibility criteria for a clinical trial written as a fulltext - char field, max length 4000

        min_age - mininum age of the enrolled patients - char field

        max_age - maximum age of the enrolled patients - char field

        gender - gender of the enrolled patients - char field

        linked - technical information, it tells whether the document has been processed by an entity linker - boolean field
    """
    nctid = models.CharField(max_length=100, primary_key=True)
    brief_title = models.CharField(max_length=4000)
    official_title = models.CharField(max_length=4000)
    description = models.CharField(max_length=4000)
    summary = models.CharField(max_length=4000)
    criteria = models.CharField(max_length=4000)
    min_age = models.CharField(max_length=100)
    max_age = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    study_type = models.CharField(max_length=1000, default='')
    linked = models.BooleanField(default=False)
    genes_extracted = models.BooleanField(default=False)
    drugs_extracted = models.BooleanField(default=False)
    pmvocab_extracted = models.BooleanField(default=False)

class Gene(models.Model):
    main_label = models.CharField(max_length=300,primary_key=True)
    family = models.ForeignKey('self',null=True, related_name='homologs', on_delete=models.SET_NULL)

class GeneLabel(models.Model):

    text = models.CharField(max_length=300)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)

class Intervention(models.Model):
    """
    This class represents a single Intevention (method of treatment)

    Fields:
    -----------

    document - foreign key to a Clinical Trial

    type - type of a treatment, char field

    name - name of a treatment, char field

    description - description of a treatment, char field
    """
    TYPES = ['Drug', 'Procedure', 'Other', 'Biological', 'Behavioral', 'Genetic', 'Radiation', 'Device', 'Diagnostic Test', 'Dietary Supplement', 'Combination Product']
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    type = models.CharField(max_length=400)
    name = models.CharField(max_length=400)
    description = models.CharField(max_length=1000)

class Condition(models.Model):
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    text = models.CharField(max_length=400)

class ArmGroup(models.Model):
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    label = models.CharField(max_length=400)
    type = models.CharField(max_length=400)
    description = models.CharField(max_length=1000)

class PrimaryOutcomes(models.Model):
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    measure = models.CharField(max_length=400)
    time_frame = models.CharField(max_length=400)
    description = models.CharField(max_length=1000)

class SecondaryOutcomes(models.Model):
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    measure = models.CharField(max_length=400)
    time_frame = models.CharField(max_length=400)
    description = models.CharField(max_length=1000)

class Keywords(models.Model):
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    text = models.CharField(max_length=400)

class MeshCondition(models.Model):
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    term = models.CharField(max_length=400)

class MeshIntervention(models.Model):
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    term = models.CharField(max_length=400)

class Entity(models.Model):
    url = models.CharField(max_length=400)
    label = models.CharField(max_length=400)

class Topic(models.Model):
    year = models.IntegerField()
    topic_no = models.IntegerField()
    disease = models.CharField(max_length=300)
    genes = models.CharField(max_length=300)
    demo = models.CharField(max_length=300)
    genes_mtm = models.ManyToManyField(Gene)
    disease_fl = models.ForeignKey(Entity, on_delete=models.CASCADE, blank=True,null=True,default=None)

class Rating(models.Model):
    document = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    pm_rel_desc = models.CharField(max_length=500)
    pm_disease_desc = models.CharField(max_length=500)
    pm_gene1_desc = models.CharField(max_length=500)
    pm_gene1_annotation_desc = models.CharField(max_length=500)
    pm_gene2_desc = models.CharField(max_length=500)
    pm_gene2_annotation_desc = models.CharField(max_length=500)
    pm_gene3_desc = models.CharField(max_length=500)
    pm_gene3_annotation_desc = models.CharField(max_length=500)
    
    ######WARNING FOR NOW PM_OTHER_DESC CONTAINS DEMOGRAPHICS DECISION, PM_DEMO_DESC DOES NOT
    pm_other_desc = models.CharField(max_length=500)
    pm_demo_desc = models.CharField(max_length=500)
    correct_condition_disease = models.CharField(max_length=20)
    positive_gene = models.BooleanField(default=False)
    positive_gene_title = models.BooleanField(default=False)
    positive_gene_criteria = models.BooleanField(default=False)
    positive_disease = models.BooleanField(default=False)
    positive_treatment = models.BooleanField(default=False)
    total_score = models.IntegerField(default=0)
    disease_score = models.FloatField(default=0)
    gene_score = models.FloatField(default=0)
    gene_boost = models.IntegerField(default=0)
    demography_score = models.IntegerField(default=0)
    treatment_score = models.FloatField(default=0)
    relevance_score = models.FloatField(default=0)
    no_treatments = models.IntegerField(default=0)

class DrugGeneLinkDetails(models.Model):
    gene = models.ForeignKey("Gene", on_delete=models.CASCADE)
    drug = models.ForeignKey("Drug", on_delete=models.CASCADE)
    impact = models.FloatField(default=1.0)
class Drug(models.Model):
    generic_name = models.CharField(max_length=400, default='', blank=True)
    trade_name = models.CharField(max_length=400, default='', blank=True)
    scientific_name = models.CharField(max_length=400, default='', blank=True)
    chemical_name = models.CharField(max_length=400, default='', blank=True)

    diseases = models.ManyToManyField(Entity, blank=True)
    genes = models.ManyToManyField(Gene, blank=True)
    gene = models.ManyToManyField(Gene, blank=True, through=DrugGeneLinkDetails, related_name='gene_drug_with_details')
    def __str__(self):
        names = DrugName.objects.filter(drug = self)
        tns = [name for name in names if name.type == 'T']
        gns = [name for name in names if name.type == 'G']
        sns = [name for name in names if name.type == 'S']
        cns = [name for name in names if name.type == 'C']
        if len(gns) != 0:
            return gns[0].name
        if len(tns) != 0:
            return tns[0].name
        if len(cns) != 0:
            return cns[0].name
        if len(sns) != 0:
            return sns[0].name
        
        return str(self.pk)
        
class PMVocab(models.Model):
    word = models.CharField(max_length=400, default='')
    def __str__(self) -> str:
        return self.word
class PMVocabLink(models.Model):
    field = models.CharField(max_length=400, null=True, default=None)
    document = models.ForeignKey(
        ClinicalTrial, on_delete=models.CASCADE, null=True, default=None)
    condition = models.ForeignKey(
        Condition, on_delete=models.CASCADE, null=True, default=None)
    intervention = models.ForeignKey(
        Intervention, on_delete=models.CASCADE, null=True, default=None)
    arm_group = models.ForeignKey(
        ArmGroup, on_delete=models.CASCADE, null=True, default=None)
    primary_outcome = models.ForeignKey(
        PrimaryOutcomes, on_delete=models.CASCADE, null=True, default=None)
    seondary_outcome = models.ForeignKey(
        SecondaryOutcomes, on_delete=models.CASCADE, null=True, default=None)
    keyword = models.ForeignKey(
        Keywords, on_delete=models.CASCADE, null=True, default=None)
    mesh_intervention = models.ForeignKey(
        MeshIntervention, on_delete=models.CASCADE, null=True, default=None)
    mesh_condition = models.ForeignKey(
        MeshCondition, on_delete=models.CASCADE, null=True, default=None)
    word = models.ForeignKey(PMVocab, on_delete=models.CASCADE)
    class Meta:
        indexes = (
            models.Index(fields=['document','word']),
        )
class DrugName(models.Model):
    DRUG_NAME_TYPES = (
        ('T', 'Trade Name'),
        ('G', 'Generic Name'),
        ('C', 'Chemical Name'),
        ('S', 'Scientific Name')
    )
    name = models.CharField(max_length=400, default='',blank=True)
    drug = models.ForeignKey(Drug, default=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=1,choices=DRUG_NAME_TYPES)
    

class EntityLink(models.Model):
    field = models.CharField(max_length=400, null=True, default=None)
    document = models.ForeignKey(
        ClinicalTrial, on_delete=models.CASCADE, null=True, default=None)
    condition = models.ForeignKey(
        Condition, on_delete=models.CASCADE, null=True, default=None)
    intervention = models.ForeignKey(
        Intervention, on_delete=models.CASCADE, null=True, default=None)
    arm_group = models.ForeignKey(
        ArmGroup, on_delete=models.CASCADE, null=True, default=None)
    primary_outcome = models.ForeignKey(
        PrimaryOutcomes, on_delete=models.CASCADE, null=True, default=None)
    seondary_outcome = models.ForeignKey(
        SecondaryOutcomes, on_delete=models.CASCADE, null=True, default=None)
    keyword = models.ForeignKey(
        Keywords, on_delete=models.CASCADE, null=True, default=None)
    mesh_intervention = models.ForeignKey(
        MeshIntervention, on_delete=models.CASCADE, null=True, default=None)
    mesh_condition = models.ForeignKey(
        MeshCondition, on_delete=models.CASCADE, null=True, default=None)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

class DrugLink(models.Model):
    field = models.CharField(max_length=400, null=True, default=None)
    document = models.ForeignKey(
        ClinicalTrial, on_delete=models.CASCADE, null=True, default=None)
    condition = models.ForeignKey(
        Condition, on_delete=models.CASCADE, null=True, default=None)
    intervention = models.ForeignKey(
        Intervention, on_delete=models.CASCADE, null=True, default=None)
    arm_group = models.ForeignKey(
        ArmGroup, on_delete=models.CASCADE, null=True, default=None)
    primary_outcome = models.ForeignKey(
        PrimaryOutcomes, on_delete=models.CASCADE, null=True, default=None)
    seondary_outcome = models.ForeignKey(
        SecondaryOutcomes, on_delete=models.CASCADE, null=True, default=None)
    keyword = models.ForeignKey(
        Keywords, on_delete=models.CASCADE, null=True, default=None)
    mesh_intervention = models.ForeignKey(
        MeshIntervention, on_delete=models.CASCADE, null=True, default=None)
    mesh_condition = models.ForeignKey(
        MeshCondition, on_delete=models.CASCADE, null=True, default=None)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)

class GeneLink(models.Model):
    field = models.CharField(max_length=400, null=True, default=None)
    document = models.ForeignKey(
        ClinicalTrial, on_delete=models.CASCADE, null=True, default=None)
    condition = models.ForeignKey(
        Condition, on_delete=models.CASCADE, null=True, default=None)
    intervention = models.ForeignKey(
        Intervention, on_delete=models.CASCADE, null=True, default=None)
    arm_group = models.ForeignKey(
        ArmGroup, on_delete=models.CASCADE, null=True, default=None)
    primary_outcome = models.ForeignKey(
        PrimaryOutcomes, on_delete=models.CASCADE, null=True, default=None)
    seondary_outcome = models.ForeignKey(
        SecondaryOutcomes, on_delete=models.CASCADE, null=True, default=None)
    keyword = models.ForeignKey(
        Keywords, on_delete=models.CASCADE, null=True, default=None)
    mesh_intervention = models.ForeignKey(
        MeshIntervention, on_delete=models.CASCADE, null=True, default=None)
    mesh_condition = models.ForeignKey(
        MeshCondition, on_delete=models.CASCADE, null=True, default=None)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)

class GeneAnnotation(models.Model):
    rating = models.ForeignKey(Rating,  on_delete=models.CASCADE)
    gene_link = models.ForeignKey(GeneLink, on_delete=models.CASCADE)    
    match = models.CharField(max_length=20)
    score = models.FloatField()
    correct = models.CharField(max_length=20)
    source = models.CharField(max_length=20)

class ConditionAnnotation(models.Model):
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    entity_link = models.ForeignKey(
        EntityLink, on_delete=models.CASCADE, null=True, default=None)
    match = models.CharField(max_length=20)
    score = models.FloatField()
    correct = models.CharField(max_length=20)
    source = models.CharField(max_length=20)
