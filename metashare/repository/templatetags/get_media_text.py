from django import template

from metashare.repository.models import corpusInfoType_model, \
    toolServiceInfoType_model, lexicalConceptualResourceInfoType_model, \
    languageDescriptionInfoType_model

register = template.Library()

class GetMediaText(template.Node):
    """
    Template tag that allows to display media types, in text,  in result page template.    
    """
    
    def __init__(self, context_var, target_context_var=None):
        """
        Initialises this template tag.
        """
        super(GetMediaText, self).__init__()
        self.context_var = template.Variable(context_var)
        self.target_context_var = target_context_var
        
    def render(self, context):
        """
        Renders media types in text
        """
        result = []
        corpus_media = self.context_var.resolve(context)
    
        if isinstance(corpus_media, corpusInfoType_model):
            media_type = corpus_media.corpusMediaType
            for corpus_info in media_type.corpustextinfotype_model_set.all():
                result.append(corpus_info.mediaType)
            if media_type.corpusAudioInfo:
                result.append(media_type.corpusAudioInfo.mediaType)
            for corpus_info in media_type.corpusvideoinfotype_model_set.all():
                result.append(corpus_info.mediaType)
            if media_type.corpusTextNgramInfo:
                result.append(media_type.corpusTextNgramInfo.mediaType)
            if media_type.corpusImageInfo:
                result.append(media_type.corpusImageInfo.mediaType)
            if media_type.corpusTextNumericalInfo:
                result.append(media_type.corpusTextNumericalInfo.mediaType)

        elif isinstance(corpus_media, lexicalConceptualResourceInfoType_model):
            lcr_media_type = corpus_media.lexicalConceptualResourceMediaType
            if lcr_media_type.lexicalConceptualResourceTextInfo:
                result.append(lcr_media_type.lexicalConceptualResourceTextInfo.mediaType)
            if lcr_media_type.lexicalConceptualResourceAudioInfo:
                result.append(lcr_media_type \
                    .lexicalConceptualResourceAudioInfo.mediaType)
            if lcr_media_type.lexicalConceptualResourceVideoInfo:
                result.append(lcr_media_type \
                    .lexicalConceptualResourceVideoInfo.mediaType)
            if lcr_media_type.lexicalConceptualResourceImageInfo:
                result.append(lcr_media_type \
                    .lexicalConceptualResourceImageInfo.mediaType)

        elif isinstance(corpus_media, languageDescriptionInfoType_model):
            ld_media_type = corpus_media.languageDescriptionMediaType
            if ld_media_type.languageDescriptionTextInfo:
                result.append(ld_media_type.languageDescriptionTextInfo.mediaType)
            if ld_media_type.languageDescriptionVideoInfo:
                result.append(ld_media_type.languageDescriptionVideoInfo.mediaType)
            if ld_media_type.languageDescriptionImageInfo:
                result.append(ld_media_type.languageDescriptionImageInfo.mediaType)

        elif isinstance(corpus_media, toolServiceInfoType_model):
            if corpus_media.inputInfo:
                result.extend(corpus_media.inputInfo \
                              .get_mediaType_display_list())
            if corpus_media.outputInfo:
                result.extend(corpus_media.outputInfo \
                              .get_mediaType_display_list())

        result = list(set(result))
        result.sort()

        # use plain text when displaying media types
        text_result = ""
        if "text" in result:
            text_result = "Text "
        if "audio" in result:
            text_result = text_result + "Audio "
        if "image" in result:
            text_result = text_result + "Image "
        if "video" in result:
            text_result = text_result + "Video "
        if "textNumerical" in result:
            text_result = text_result + "Text Numerical"
        if "textNgram" in result:
            text_result = text_result + "Text N-Gram"
        
        if self.target_context_var is not None:
            if text_result == "":
                return text_result
            return "<dt>Media Type<dd>%s</dd></dt>" % text_result
        else:
            context[self.target_context_var] = text_result
            return ""

    def get_media_text(parser, token):
        """
        Use it like this: {% load_languages object.resourceComponentType.as_subclass %}
        """
        tokens = token.contents.split()
        if len(tokens) != 2:
            _msg = "%r tag accepts exactly two arguments" % tokens[0]
            raise template.TemplateSyntaxError(_msg)
        
        return GetMediaText(tokens[1])

    def get_m_text_into_var(parser, token):
        tokens = token.contents.split()
        if len(tokens) != 3:
            _msg = "%r tag accepts exactly three arguments" % tokens[0]
            raise template.TemplateSyntaxError(_msg)
        return GetMediaText(*tokens[1:])

    register.tag('get_media_text', get_media_text)
    register.tag('get_m_text_into_var', get_m_text_into_var)