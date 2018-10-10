from django import template

from metashare.repository.models import corpusInfoType_model, \
    toolServiceInfoType_model, lexicalConceptualResourceInfoType_model, \
    languageDescriptionInfoType_model


register = template.Library()


@register.assignment_tag
def get_resource_media_types(resource_info_type):
    """
    Template tag that allows to display media types in result page template.    

    Use it like this: {% get_resource_media_types object.resourceComponentType.as_subclass %}
    """
    result = []
    types_mapping = [
        ("text", "Text"),
        ("audio", "Audio"),
        ("image", "Image"),
        ("video", "Video"),
        ("textNumerical", "Text Numerical"),
        ("textNgram", "Text N-Gram"),
    ]

    if isinstance(resource_info_type, corpusInfoType_model):
        resource_info_type = resource_info_type.corpusMediaType
        for corpus_info in resource_info_type.corpustextinfotype_model_set.all():
            result.append(corpus_info.mediaType)
        if resource_info_type.corpusAudioInfo:
            result.append(resource_info_type.corpusAudioInfo.mediaType)
        for corpus_info in resource_info_type.corpusvideoinfotype_model_set.all():
            result.append(corpus_info.mediaType)
        if resource_info_type.corpusTextNgramInfo:
            result.append(resource_info_type.corpusTextNgramInfo.mediaType)
        if resource_info_type.corpusImageInfo:
            result.append(resource_info_type.corpusImageInfo.mediaType)
        if resource_info_type.corpusTextNumericalInfo:
            result.append(resource_info_type.corpusTextNumericalInfo.mediaType)

    elif isinstance(resource_info_type, lexicalConceptualResourceInfoType_model):
        lcr_resource_info_type = resource_info_type.lexicalConceptualResourceMediaType
        if lcr_resource_info_type.lexicalConceptualResourceTextInfo:
            result.append(lcr_resource_info_type.lexicalConceptualResourceTextInfo.mediaType)
        if lcr_resource_info_type.lexicalConceptualResourceAudioInfo:
            result.append(lcr_resource_info_type \
                .lexicalConceptualResourceAudioInfo.mediaType)
        if lcr_resource_info_type.lexicalConceptualResourceVideoInfo:
            result.append(lcr_resource_info_type \
                .lexicalConceptualResourceVideoInfo.mediaType)
        if lcr_resource_info_type.lexicalConceptualResourceImageInfo:
            result.append(lcr_resource_info_type \
                .lexicalConceptualResourceImageInfo.mediaType)

    elif isinstance(resource_info_type, languageDescriptionInfoType_model):
        ld_resource_info_type = resource_info_type.languageDescriptionMediaType
        if ld_resource_info_type.languageDescriptionTextInfo:
            result.append(ld_resource_info_type.languageDescriptionTextInfo.mediaType)
        if ld_resource_info_type.languageDescriptionVideoInfo:
            result.append(ld_resource_info_type.languageDescriptionVideoInfo.mediaType)
        if ld_resource_info_type.languageDescriptionImageInfo:
            result.append(ld_resource_info_type.languageDescriptionImageInfo.mediaType)

    elif isinstance(resource_info_type, toolServiceInfoType_model):
        if resource_info_type.inputInfo:
            result.extend(resource_info_type.inputInfo \
                            .get_mediaType_display_list())
        if resource_info_type.outputInfo:
            result.extend(resource_info_type.outputInfo \
                            .get_mediaType_display_list())

    return [
        text for resource_info_type, text in types_mapping
        if resource_info_type in result
    ]
