from django import template

from metashare.repository.models import corpusInfoType_model, \
    toolServiceInfoType_model, lexicalConceptualResourceInfoType_model, \
    languageDescriptionInfoType_model


register = template.Library()


@register.assignment_tag
def get_resource_languages(resource_info_type):
    """
    Template tag that allows to display languages in result page template.

    Use it like this: {% load_languages object.resourceComponentType.as_subclass %}
    """
    result = set()

    if isinstance(resource_info_type, corpusInfoType_model):
        resource_info_type = resource_info_type.corpusMediaType
        for corpus_info in resource_info_type.corpustextinfotype_model_set.all():
            result.update([lang.languageName for lang in
                            corpus_info.languageinfotype_model_set.all()])
        if resource_info_type.corpusAudioInfo:
            result.update([lang.languageName for lang in
                            resource_info_type.corpusAudioInfo.languageinfotype_model_set.all()])
        for corpus_info in resource_info_type.corpusvideoinfotype_model_set.all():
            result.update([lang.languageName for lang in
                            corpus_info.languageinfotype_model_set.all()])
        if resource_info_type.corpusTextNgramInfo:
            result.update([lang.languageName for lang in
                        resource_info_type.corpusTextNgramInfo.languageinfotype_model_set.all()])
        if resource_info_type.corpusImageInfo:
            result.update([lang.languageName for lang in
                            resource_info_type.corpusImageInfo.languageinfotype_model_set.all()])

    elif isinstance(resource_info_type, lexicalConceptualResourceInfoType_model):
        lcr_resource_info_type = resource_info_type.lexicalConceptualResourceMediaType
        if lcr_resource_info_type.lexicalConceptualResourceAudioInfo:
            result.update([lang.languageName for lang in lcr_resource_info_type \
                    .lexicalConceptualResourceAudioInfo.languageinfotype_model_set.all()])
        if lcr_resource_info_type.lexicalConceptualResourceTextInfo:
            result.update([lang.languageName for lang in lcr_resource_info_type \
                    .lexicalConceptualResourceTextInfo.languageinfotype_model_set.all()])
        if lcr_resource_info_type.lexicalConceptualResourceVideoInfo:
            result.update([lang.languageName for lang in lcr_resource_info_type \
                    .lexicalConceptualResourceVideoInfo.languageinfotype_model_set.all()])
        if lcr_resource_info_type.lexicalConceptualResourceImageInfo:
            result.update([lang.languageName for lang in lcr_resource_info_type \
                    .lexicalConceptualResourceImageInfo.languageinfotype_model_set.all()])

    elif isinstance(resource_info_type, languageDescriptionInfoType_model):
        ld_resource_info_type = resource_info_type.languageDescriptionMediaType
        if ld_resource_info_type.languageDescriptionTextInfo:
            result.update([lang.languageName for lang in ld_resource_info_type \
                        .languageDescriptionTextInfo.languageinfotype_model_set.all()])
        if ld_resource_info_type.languageDescriptionVideoInfo:
            result.update([lang.languageName for lang in ld_resource_info_type \
                        .languageDescriptionVideoInfo.languageinfotype_model_set.all()])
        if ld_resource_info_type.languageDescriptionImageInfo:
            result.update([lang.languageName for lang in ld_resource_info_type \
                        .languageDescriptionImageInfo.languageinfotype_model_set.all()])

    elif isinstance(resource_info_type, toolServiceInfoType_model):
        if resource_info_type.inputInfo:
            result.update(resource_info_type.inputInfo.languageName)
        if resource_info_type.outputInfo:
            result.update(resource_info_type.outputInfo.languageName)

    return sorted(result)

