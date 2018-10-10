<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns="http://www.ilsp.gr/META-XMLSchema" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns:dc="http://purl.org/dc/elements/1.1/" 
xmlns:dcterms="http://purl.org/dc/terms/" xmlns:olac="http://www.language-archives.org/OLAC/1.1/" 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:date="http://exslt.org/dates-and-times" 
xmlns:xalan="http://xml.apache.org/xslt" exclude-result-prefixes="date xalan dc olac dcterms">

	<xsl:output method="xml" encoding="UTF-8" indent="yes" xalan:indent-amount="4"/>

	<xsl:template match="*">
		<xsl:value-of select="."/>
		<xsl:text>
</xsl:text><!-- new line -->
	</xsl:template>
	
	<xsl:template name="mediaTypeSpecific">
		<xsl:param name="mediaType"/>
		<xsl:param name="componentType"/>
		<mediaType>
			<xsl:value-of select="$mediaType"/>
		</mediaType>
		<lingualityInfo>
			<xsl:choose>
				<xsl:when test="count(../dc:language)>2">
					<lingualityType>multilingual</lingualityType>
				</xsl:when>
				<xsl:when test="count(../dc:language)=2">
					<lingualityType>bilingual</lingualityType>
				</xsl:when>
				<xsl:otherwise>
					<lingualityType>monolingual</lingualityType>
				</xsl:otherwise>
			</xsl:choose>
		</lingualityInfo>
		<xsl:choose>
			<xsl:when test="../dc:language">
				<xsl:for-each select="../dc:language">
					<languageInfo>
						<xsl:choose>
							<xsl:when test="@olac:code!='zxx'"><!--No linguistic content-->
								<languageId>
									<xsl:choose>
										<xsl:when test="@olac:code"><xsl:value-of select="@olac:code"/></xsl:when>
										<xsl:otherwise>und</xsl:otherwise><!--undefined-->
									</xsl:choose>
								</languageId>
								<languageName>
									<xsl:choose>
										<xsl:when test=".!=''"><xsl:value-of select="."/></xsl:when>
										<xsl:otherwise><xsl:value-of select="@olac:code"/> language</xsl:otherwise>
									</xsl:choose>
								</languageName>
								
							</xsl:when>
							<xsl:otherwise>
								<languageId>
									<xsl:text>und</xsl:text><!--undefined-->
								</languageId>
								<languageName>
									<xsl:value-of select="."/>
								</languageName>
							</xsl:otherwise>
						</xsl:choose>
					</languageInfo>
				</xsl:for-each>
			</xsl:when>
			<xsl:when test="$mediaType='text' or ($componentType='corpus' and $mediaType='audio')">
				<languageInfo>
					<languageId>
						<xsl:text>und</xsl:text><!--undefined-->
					</languageId>
					<languageName>
						<xsl:text>language</xsl:text>
					</languageName>
				</languageInfo>
			</xsl:when>
		</xsl:choose>
		<xsl:choose>
			<xsl:when test="$componentType='corpus' and $mediaType='audio'">
				<audioSizeInfo>
					<sizeInfo>
						<size>
							<xsl:choose>
								<xsl:when test="../dcterms:extent"><xsl:value-of select="../dcterms:extent"/></xsl:when>
								<xsl:otherwise>Size information unidentified or non representable</xsl:otherwise>
							</xsl:choose>
						</size>
					<sizeUnit>other</sizeUnit>
				</sizeInfo>
				</audioSizeInfo>
			</xsl:when>
			<xsl:otherwise>
				<sizeInfo>
					<size>
						<xsl:choose>
							<xsl:when test="../dcterms:extent"><xsl:value-of select="../dcterms:extent"/></xsl:when>
							<xsl:otherwise>Size information unidentified or non representable</xsl:otherwise>
						</xsl:choose>
					</size>
					<sizeUnit>other</sizeUnit>
				</sizeInfo>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:if test="$componentType='lexicalConceptual' and $mediaType='video'">
			<videoContentInfo>
				<xsl:choose>
					<xsl:when test="../dc:subject">
						<xsl:for-each select="../dc:subject">
							<typeOfVideoContent>
								<xsl:choose>
									<xsl:when test=".!=''">
										<xsl:value-of select="."/>
									</xsl:when>
									<xsl:when test="@xsi:type='olac:discourse-type'">
										<xsl:value-of select="@olac:code"/>
									</xsl:when>
								</xsl:choose>
							</typeOfVideoContent>
						</xsl:for-each>
					</xsl:when>
					<xsl:when test="../dc:type and @xsi:type='olac:discourse-type'">
						<typeOfVideoContent>
							<xsl:choose>
								<xsl:when test="string(../dc:type)!=''">
									<xsl:value-of select="../dc:type"/>
								</xsl:when>
								<xsl:otherwise>
									<xsl:value-of select="../dc:type/@olac:code"/>
								</xsl:otherwise>
							</xsl:choose>
						</typeOfVideoContent>
					</xsl:when>
					<xsl:otherwise>
						<typeOfVideoContent>No type of video content is available</typeOfVideoContent>
					</xsl:otherwise>
				</xsl:choose>
			</videoContentInfo>			
		</xsl:if>
		<xsl:for-each select="../dc:format">
			<xsl:choose>
				<xsl:when test="$mediaType='text'">
					<textFormatInfo>
						<mimeType>
							<xsl:value-of select="."/>
						</mimeType>
					</textFormatInfo>
				</xsl:when>
				<xsl:when test="$mediaType='audio'">
					<audioFormatInfo>
						<mimeType>
							<xsl:value-of select="."/>
						</mimeType>
					</audioFormatInfo>
				</xsl:when>
				<xsl:when test="$mediaType='image'">
					<imageFormatInfo>
						<mimeType>
							<xsl:value-of select="."/>
						</mimeType>
					</imageFormatInfo>
				</xsl:when>
				<xsl:when test="$mediaType='video'">
					<videoFormatInfo>
						<mimeType>
							<xsl:value-of select="."/>
						</mimeType>
					</videoFormatInfo>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
		
		<xsl:for-each select="../dc:spatial">
			<geographicCoverageInfo>
				<geographicCoverage>
					<xsl:value-of select="string(.)"/>
				</geographicCoverage>
			</geographicCoverageInfo>
		</xsl:for-each>
		
		<xsl:if test="$componentType='corpus' and ../dc:source">
			<creationInfo>
				<xsl:for-each select="../dc:source">
					<originalSource>
						<targetResourceNameURI>
							<xsl:value-of select="string(.)"/>
						</targetResourceNameURI>
					</originalSource>
				</xsl:for-each>
			</creationInfo>
		</xsl:if>
		
		<xsl:if test="$componentType='languageDescription' and ($mediaType='video' or $mediaType='image')">
			<linkToOtherMediaInfo>
				<otherMedia>text</otherMedia>
			</linkToOtherMediaInfo>
			<xsl:if test="count(dc:type[@xsi:type='dcterms:DCMIType'])=3">
				<linkToOtherMediaInfo>
					<xsl:if test="$mediaType='video'">
						<otherMedia>image</otherMedia>
					</xsl:if>
					<xsl:if test="$mediaType='image'">
						<otherMedia>video</otherMedia>
					</xsl:if>
				</linkToOtherMediaInfo>
			</xsl:if>
		</xsl:if>
	</xsl:template>


	<!-- <xsl:template match="*[local-name()='metadataInfo']">-->
	<xsl:template match="*[local-name()='olac']">
	<xsl:text>
</xsl:text>
		<resourceInfo>
		<xsl:attribute name="xsi:schemaLocation">http://www.ilsp.gr/META-XMLSchema http://metashare.ilsp.gr/META-XMLSchema/v3.0/META-SHARE-Resource.xsd</xsl:attribute>
			<identificationInfo>
				<xsl:choose>
					<xsl:when test="not(dc:title/@xml:lang) or (dcterms:alternative and not(dcterms:alternative/@xml:lang))">
						<resourceName>
							<xsl:for-each select="dc:title">
								<xsl:value-of select="."/>
								<xsl:if test="not(position()=last())">, </xsl:if>
							</xsl:for-each>
							<xsl:if test="dcterms:alternative">
								<xsl:text>
		</xsl:text>
							</xsl:if>
							<xsl:for-each select="dcterms:alternative">
								<xsl:value-of select="."/>
								<xsl:if test="not(position()=last())">, </xsl:if>
							</xsl:for-each>
						</resourceName>
					</xsl:when>
					<xsl:otherwise>
						<xsl:for-each select="dc:title">
							<resourceName>
								<xsl:attribute name ="lang">
									<xsl:value-of select ="@xml:lang" />
								</xsl:attribute>
								<xsl:value-of select="(.)"/>
							</resourceName>
						</xsl:for-each>
						<xsl:for-each select="dcterms:alternative">
							<resourceName>
								<xsl:attribute name ="lang">
									<xsl:value-of select ="@xml:lang" />
								</xsl:attribute>
								<xsl:value-of select="(.)"/>
							</resourceName>
						</xsl:for-each>
					</xsl:otherwise>
				</xsl:choose>

				<description><!-- dc:description, dcterms:abstract, dcterms:tableOfContents -->
					<xsl:for-each select="dc:description">
						<xsl:apply-templates select="."/>
					</xsl:for-each>

					<xsl:for-each select="dcterms:abstract">
						<xsl:apply-templates select="."/>
					</xsl:for-each>

					<xsl:for-each select="dcterms:tableOfContents">
						<xsl:apply-templates select="."/>
					</xsl:for-each>
				</description>
				<xsl:for-each select="dcterms:URI">
					<url>
						<xsl:value-of select="string(.)"/>
					</url>
				</xsl:for-each>
				<metaShareId>NOT_DEFINED_FOR_V2</metaShareId>
				<xsl:for-each select="dc:identifier">
					<xsl:choose>
						<xsl:when test="contains(string(.), 'http')">
							<url>
								<xsl:value-of select="string(.)"/>
							</url>
						</xsl:when>
						<xsl:otherwise>
							<identifier>
								<xsl:value-of select="string(.)"/>
							</identifier>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:for-each>

			</identificationInfo>

			<distributionInfo>
				<availability>notAvailableThroughMetaShare</availability>
				<xsl:if test="dc:publisher">
					<licenceInfo>
					<licence>other</licence>
						<xsl:for-each select="dc:publisher">
							<distributionRightsHolder>
								<xsl:choose>
									<xsl:when test="contains((.), 'University') or contains((.), 'Department') or string-length(normalize-space(.)) - string-length(translate(normalize-space(.),' ','')) +1 &gt; 3">
										<organizationInfo>
											<organizationName>
												<xsl:value-of select="string(.)"/>
											</organizationName>
											<communicationInfo>
												<email>default@fake-email.com</email>
											</communicationInfo>
										</organizationInfo>
									</xsl:when>
									<xsl:otherwise>
										<personInfo>
											<xsl:choose>
												<xsl:when test="contains((.), ',')">
													<surname>
														<xsl:value-of select="substring-before(translate(normalize-space(.),' ',''), ',')"/>
													</surname>
													<givenName>
														<xsl:value-of select="substring-after(translate(normalize-space(.),' ',''), ',')"/>
													</givenName>
												</xsl:when>
												<xsl:otherwise>
													<surname>
														<xsl:value-of select="string(.)"/>
													</surname>
												</xsl:otherwise>
											</xsl:choose>
											<communicationInfo>
												<email>default@fake-email.com</email>
											</communicationInfo>
										</personInfo>
									</xsl:otherwise>
								</xsl:choose>

							</distributionRightsHolder>
						</xsl:for-each>
					</licenceInfo>
				</xsl:if>
		   	</distributionInfo>
			
			
			<xsl:choose>
				<xsl:when test="dc:contributor[@xsi:type='olac:role']/@olac:code='depositor'">
					<xsl:for-each select="dc:contributor[@olac:code='depositor']">
						<contactPerson>
							<xsl:choose>
								<xsl:when test="contains(.,',')">
									<surname>
										<xsl:value-of select="substring-before(translate(normalize-space(.),' ',''), ',')"/></surname>
									<givenName>
										<xsl:value-of select="substring-after(translate(normalize-space(.),' ',''), ',')"/>
									</givenName>
								</xsl:when>
								<xsl:otherwise>
									<surname>
										<xsl:value-of select="."/></surname>
								</xsl:otherwise>
							</xsl:choose>
							<communicationInfo>
								<email>default@fake-email.com</email>
							</communicationInfo>
						</contactPerson>
					</xsl:for-each>
				</xsl:when>
				<xsl:otherwise>
					<contactPerson>
						<surname>contact person not available</surname>
						<communicationInfo>
							<email>default@fake-email.com</email>
						</communicationInfo>
					</contactPerson>
				</xsl:otherwise>
			</xsl:choose>	
			
			<metadataInfo>
				<metadataCreationDate><!-- current timestamp -->
					<xsl:value-of select="substring(date:date(), 1, 10)"/>
				</metadataCreationDate>
			</metadataInfo>			

			<xsl:if test="dcterms:bibliographicCitation">
					<resourceDocumentationInfo>
					  <documentation>
						<documentUnstructured>
							<xsl:for-each select="dcterms:bibliographicCitation">
								<xsl:value-of select="string(.)"/>
								<xsl:if test="not(position()=last())">, </xsl:if>
							</xsl:for-each>
						</documentUnstructured>
					  </documentation>
					</resourceDocumentationInfo>
			</xsl:if>
			
			<xsl:if test="dc:creator or dcterms:created">
				<resourceCreationInfo>
					<xsl:for-each select="dc:creator">
						<resourceCreator>
							<xsl:choose>
								<xsl:when test="contains((.), 'University') or contains((.), 'Department') or string-length(normalize-space(.)) - string-length(translate(normalize-space(.),' ','')) +1 &gt; 3">
									<organizationInfo>
										<organizationName>
											<xsl:value-of select="string(.)"/>
										</organizationName>
										<communicationInfo>
											<email>default@fake-email.com</email>
										</communicationInfo>
									</organizationInfo>
								</xsl:when>
								<xsl:otherwise>
									<personInfo>
										<xsl:choose>
											<xsl:when test="contains((.), ',')">
												<surname>
													<xsl:value-of select="substring-before(translate(normalize-space(.),' ',''), ',')"/></surname>
												<givenName>
													<xsl:value-of select="substring-after(translate(normalize-space(.),' ',''), ',')"/>
												</givenName>
											</xsl:when>
											<xsl:otherwise>
												<surname>
													<xsl:value-of select="string(.)"/>
												</surname>
											</xsl:otherwise>
										</xsl:choose>
										<communicationInfo>
											<email>default@fake-email.com</email>
										</communicationInfo>
									</personInfo>
								</xsl:otherwise>
							</xsl:choose>
						</resourceCreator>
					</xsl:for-each>
					<xsl:if test="dcterms:created">
						<xsl:if test="(starts-with(dcterms:created, 1) or starts-with(dcterms:created, 2))">
							<creationStartDate>
							<xsl:choose>
								<xsl:when test="(string-length(dcterms:created)=10)"><!-- if dcterms:created is a full date -->
									<xsl:value-of select="string(dcterms:created)"/>
								</xsl:when>
								<xsl:when test="string-length(dcterms:created)=4 and (starts-with(dcterms:created, 1) or starts-with(dcterms:created, 2))"><!-- otherwise, keep the year
	-->
									<xsl:value-of select="concat(dcterms:created, '-01-01')"/>
									
								</xsl:when>
								<xsl:otherwise>
									<xsl:value-of select="substring-before(dcterms:created,'T')" />
								</xsl:otherwise>
							</xsl:choose>
							</creationStartDate>
						</xsl:if>
					</xsl:if>
				</resourceCreationInfo>
			</xsl:if>

			<xsl:variable name="linguisticType" select="dc:type[@xsi:type='olac:linguistic-type']/@olac:code"/><!-- resource type -->

			<resourceComponentType>
				<xsl:choose>
					<xsl:when test="not($linguisticType)"><!-- if no linguistic type, apply templates for dcmi type software/service -->
						<toolServiceInfo>
							<resourceType>toolService</resourceType>
							<toolServiceType>
							<xsl:choose>
								<xsl:when test="dc:type[@xsi:type='dcterms:DCMIType']='service'">service</xsl:when>
								<xsl:otherwise>tool</xsl:otherwise><!-- cases: software or other -->
							</xsl:choose>
							</toolServiceType>

							<xsl:if test="dc:source">
								<toolServiceCreationInfo>
									<xsl:for-each select="dc:source">
										<originalSource>
											<targetResourceNameURI>
												<xsl:value-of select="string(.)"/>
											</targetResourceNameURI>
										</originalSource>
									</xsl:for-each>
								</toolServiceCreationInfo>
							</xsl:if>
							
							<languageDependent>
								<xsl:choose>
									<xsl:when test="dc:language">
										<xsl:text>true</xsl:text>
									</xsl:when>
									<xsl:otherwise>
										<xsl:text>false</xsl:text>
									</xsl:otherwise>
								</xsl:choose>
							</languageDependent>


						</toolServiceInfo>
					</xsl:when>
					<xsl:otherwise>
						<xsl:choose>
							<xsl:when test="contains($linguisticType, 'primary_text')">
								<corpusInfo>
									<resourceType>corpus</resourceType>
									<corpusMediaType>
										<xsl:for-each select="dc:type[@xsi:type='dcterms:DCMIType']">
											<xsl:choose>
												<xsl:when test="contains(., 'Text') or contains(., 'Dataset') or contains(., 'Collection')">
													<corpusTextInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'text'"/>
															<xsl:with-param name="componentType" select="'corpus'"/>
														</xsl:call-template>
													</corpusTextInfo>
												</xsl:when>
												<xsl:when test="contains(., 'Sound')">
													<corpusAudioInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'audio'"/>
															<xsl:with-param name="componentType" select="'corpus'"/>
														</xsl:call-template>
													</corpusAudioInfo>
												</xsl:when>
												<xsl:when test="contains(., 'Image') or contains(., 'StillImage')">
													<corpusImageInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'image'"/>
															<xsl:with-param name="componentType" select="'corpus'"/>
														</xsl:call-template>
													</corpusImageInfo>
												</xsl:when>
												<xsl:when test="contains(., 'MovingImage') or contains(., 'InteractiveResource')">
													<corpusVideoInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'video'"/>
															<xsl:with-param name="componentType" select="'corpus'"/>
														</xsl:call-template>
													</corpusVideoInfo>
												</xsl:when>
											</xsl:choose>
										</xsl:for-each>
									</corpusMediaType>
								</corpusInfo>
							</xsl:when>
							<xsl:when test="contains($linguisticType, 'language_description')">
								<languageDescriptionInfo>
									<resourceType>languageDescription</resourceType>
									<languageDescriptionType>other</languageDescriptionType>

									<xsl:if test="dc:source">
										<creationInfo>
											<xsl:for-each select="dc:source">
												<originalSource>
													<targetResourceNameURI>
														<xsl:value-of select="string(.)"/>
													</targetResourceNameURI>
												</originalSource>
											</xsl:for-each>
										</creationInfo>
									</xsl:if>

									<languageDescriptionMediaType>
										<xsl:for-each select="dc:type[@xsi:type='dcterms:DCMIType']">
											<xsl:choose>
												<xsl:when test="contains(., 'Text') or contains(., 'Dataset') or contains(., 'Collection')">
													<languageDescriptionTextInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'text'"/>
															<xsl:with-param name="componentType" select="'languageDescription'"/>
														</xsl:call-template>
													</languageDescriptionTextInfo>
												</xsl:when>
												<xsl:when test="contains(., 'Image') and not(contains(., 'MovingImage'))">
													<languageDescriptionImageInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'image'"/>
															<xsl:with-param name="componentType" select="'languageDescription'"/>
														</xsl:call-template>
													</languageDescriptionImageInfo>
												</xsl:when>
												<xsl:when test="contains(., 'MovingImage') or contains(., 'InteractiveResource')">
													<languageDescriptionVideoInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'video'"/>
															<xsl:with-param name="componentType" select="'languageDescription'"/>
														</xsl:call-template>
													</languageDescriptionVideoInfo>
												</xsl:when>
											</xsl:choose>
										</xsl:for-each>
									</languageDescriptionMediaType>
								</languageDescriptionInfo>
							</xsl:when>
							<xsl:when test="contains($linguisticType, 'lexicon')">
								<lexicalConceptualResourceInfo>
									<resourceType>lexicalConceptualResource</resourceType>
									<lexicalConceptualResourceType>lexicon</lexicalConceptualResourceType>

									<xsl:if test="dc:source">
										<creationInfo>
											<xsl:for-each select="dc:source">
												<originalSource>
													<targetResourceNameURI>
														<xsl:value-of select="string(.)"/>
													</targetResourceNameURI>
												</originalSource>
											</xsl:for-each>
										</creationInfo>
									</xsl:if>

									<lexicalConceptualResourceMediaType>
										<xsl:for-each select="dc:type[@xsi:type='dcterms:DCMIType']">
											<xsl:choose>
												<xsl:when test="contains(., 'Text') or contains(., 'Dataset') or contains(., 'Collection')">
													<lexicalConceptualResourceTextInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'text'"/>
															<xsl:with-param name="componentType" select="'lexicalConceptual'"/>
														</xsl:call-template>
													</lexicalConceptualResourceTextInfo>
												</xsl:when>
												<xsl:when test="contains(., 'Sound')">
													<lexicalConceptualResourceAudioInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'audio'"/>
															<xsl:with-param name="componentType" select="'lexicalConceptual'"/>
														</xsl:call-template>
													</lexicalConceptualResourceAudioInfo>
												</xsl:when>
												<xsl:when test="contains(., 'Image') or contains(., 'StillImage')">
													<lexicalConceptualResourceImageInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'image'"/>
															<xsl:with-param name="componentType" select="'lexicalConceptual'"/>
														</xsl:call-template>
													</lexicalConceptualResourceImageInfo>
												</xsl:when>
												<xsl:when test="contains(., 'MovingImage') or contains(., 'InteractiveResource')">
													<lexicalConceptualResourceVideoInfo>
														<xsl:call-template name="mediaTypeSpecific">
															<xsl:with-param name="mediaType" select="'video'"/>
															<xsl:with-param name="componentType" select="'lexicalConceptual'"/>
														</xsl:call-template>
													</lexicalConceptualResourceVideoInfo>
												</xsl:when>
											</xsl:choose>
										</xsl:for-each>
									</lexicalConceptualResourceMediaType>
								</lexicalConceptualResourceInfo>
							</xsl:when>
						</xsl:choose>
					</xsl:otherwise>
				</xsl:choose>
			</resourceComponentType>
		</resourceInfo>
	</xsl:template>
</xsl:stylesheet>
