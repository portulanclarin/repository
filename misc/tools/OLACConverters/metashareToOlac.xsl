<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:olac="http://www.language-archives.org/OLAC/1.1/" 
xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" 
xmlns:ms="http://www.ilsp.gr/META-XMLSchema" xmlns:xalan="http://xml.apache.org/xslt" exclude-result-prefixes="ms xalan" >

    <xsl:output method="xml" encoding="UTF-8" indent="yes" xalan:indent-amount="4"/>
	<xsl:template match="ms:identificationInfo">

		<xsl:for-each select="ms:resourceName">
			<dc:title>
			<xsl:attribute name ="xml:lang">
					<xsl:value-of select ="@lang" />
				</xsl:attribute>
				<xsl:value-of select="(.)"/>
			</dc:title>
		</xsl:for-each>

		<xsl:for-each select="ms:description">
			<dc:description>
			<xsl:attribute name ="xml:lang">
					<xsl:value-of select ="@lang" />
				</xsl:attribute>
				<xsl:value-of select="(.)"/>
				<xsl:if test="../ms:url">
					<xsl:text>
More info at </xsl:text><xsl:value-of select="../ms:url"/>
				</xsl:if>
			</dc:description>

		</xsl:for-each>

		<xsl:for-each select="ms:resourceShortName">
			<dcterms:alternative>
			<xsl:attribute name ="xml:lang">
					<xsl:value-of select ="@lang" />
				</xsl:attribute>
				<xsl:value-of select="(.)"/>
			</dcterms:alternative>
		</xsl:for-each>

		<xsl:if test="ms:identifier">
			<dc:identifier xsi:type="dcterms:URI">
				<xsl:value-of select="ms:identifier"/>
			</dc:identifier>
		</xsl:if>
	</xsl:template>

	<xsl:template match="ms:resourceComponentType//ms:resourceType">
		<xsl:if test="not(parent::ms:inputInfo) and not(parent::ms:outputInfo)">
			<xsl:choose>
				<xsl:when test="*|node()='corpus'">
					<dc:type xsi:type="olac:linguistic-type" olac:code="primary_text"/>
					 <dc:subject>
					 <xsl:text>language resources, </xsl:text>
					 <xsl:value-of select="../../ms:corpusInfo/ms:corpusMediaType//ms:lingualityInfo/ms:lingualityType"/>
					 <xsl:text> corpus</xsl:text>
					 <xsl:if test="//ms:subject_topic">
						<xsl:text>, </xsl:text>
						<xsl:value-of select="//ms:subject_topic"/>
					 </xsl:if>
					 <xsl:if test="//ms:annotationInfo">
						<xsl:text>, annotated with: </xsl:text>
						<xsl:value-of select="//ms:annotationInfo/ms:annotationType"/>
					 </xsl:if>
				  </dc:subject>
				</xsl:when>
				<xsl:when test="*|node()='lexicalConceptualResource'">
					<dc:type xsi:type="olac:linguistic-type" olac:code="lexicon"/>
					<dc:subject>
						<xsl:text>language resources, </xsl:text>
						<xsl:value-of select="../../ms:lexicalConceptualResourceInfo/ms:lexicalConceptualResourceMediaType//ms:lingualityInfo/ms:lingualityType"/>
						<xsl:text> lexical conceptual resource, </xsl:text>
						<xsl:value-of select="../../ms:lexicalConceptualResourceInfo/ms:lexicalConceptualResourceType"/>
					</dc:subject>
				</xsl:when>
				<xsl:when test="*|node()='languageDescription'">
					<dc:type xsi:type="olac:linguistic-type" olac:code="language_description"/>
					<dc:subject>
						<xsl:text>language resources, </xsl:text>
						<xsl:value-of select="../../ms:languageDescriptionInfo/ms:languageDescriptionMediaType//ms:lingualityInfo/ms:lingualityType"/>
						<xsl:text> language description </xsl:text>
						<xsl:value-of select="../../ms:languageDescriptionInfo/ms:languageDescriptionType"/>
					  </dc:subject>
				</xsl:when>
				<xsl:when test="*|node()='toolService'">
					<xsl:choose>
						<xsl:when test="../ms:toolServiceType = 'service'">
							<dc:type>
								<xsl:attribute name="xsi:type">
									<xsl:text>dcterms:DCMIType</xsl:text>
								</xsl:attribute>
								<xsl:text>Service</xsl:text>
							</dc:type>
						</xsl:when>
						<xsl:otherwise>
							<dc:type>
								<xsl:attribute name="xsi:type">
									<xsl:text>dcterms:DCMIType</xsl:text>
								</xsl:attribute>
								<xsl:text>Software</xsl:text>
							</dc:type>
						</xsl:otherwise>
					</xsl:choose>
					<dc:subject>
						<xsl:text>language resources, </xsl:text>
						<xsl:choose>
							<xsl:when test="../languageDependent='yes'">
								<xsl:text>language dependent </xsl:text>
							</xsl:when>
							<xsl:otherwise>
								<xsl:text>language independent </xsl:text>
							</xsl:otherwise>
						</xsl:choose>
						<xsl:value-of select="../../ms:toolServiceInfo/ms:toolServiceType"/>
						<xsl:if test="../../ms:toolServiceInfo/ms:toolServiceSubtype">
							<xsl:text>, </xsl:text><xsl:value-of select="../../ms:toolServiceInfo/ms:toolServiceSubtype"/>
						</xsl:if>
					</dc:subject>
				</xsl:when>
			</xsl:choose>
		</xsl:if>
	</xsl:template>

	<xsl:template match="//ms:mediaType">
		<xsl:if test="not(parent::ms:inputInfo) and not(parent::ms:outputInfo)">
			<dc:type xsi:type="dcterms:DCMIType">
				<xsl:choose>
					<xsl:when test="*|node()='text' or *|node()='textNgram' or *|node()='textNumerical'">
						<xsl:text>Text</xsl:text>
					</xsl:when>
					<xsl:when test="*|node()='audio'">
						<xsl:text>Sound</xsl:text>
					</xsl:when>
					<xsl:when test="*|node()='video'">
						<xsl:text>MovingImage</xsl:text>
					</xsl:when>
					<xsl:when test="*|node()='image'">
						<xsl:text>Image</xsl:text>
					</xsl:when>
				</xsl:choose>
			</dc:type>
		</xsl:if>
	</xsl:template>

	<xsl:template match="//ms:relationInfo/ms:relatedResource/ms:targetResourceNameURI">
		<dc:relation>
			<xsl:apply-templates select="../../ms:relationType"/>: <xsl:apply-templates select="*|node()"/>
		</dc:relation>
	</xsl:template>

	<xsl:template match="//ms:distributionAccessMedium">
		<dcterms:medium>
			<xsl:apply-templates select="*|node()"/>
		</dcterms:medium>
	</xsl:template>

	<xsl:key name="languageName" match="//ms:languageInfo" use="."/>
	<xsl:key name="size" match="//ms:sizeInfo" use="."/>
	<xsl:key name="mimeType" match="ms:resourceComponentType//ms:mimeType" use="."/>



	<xsl:template match="ms:resourceInfo">
		<xsl:text>
</xsl:text>		
		<olac:olac>
		<xsl:attribute name="xsi:schemaLocation">http://purl.org/dc/elements/1.1/ http://www.language-archives.org/OLAC/1.1/dc.xsd http://purl.org/dc/terms/ http://www.language-archives.org/OLAC/1.1/dcterms.xsd http://www.language-archives.org/OLAC/1.1/ http://www.language-archives.org/OLAC/1.1/olac.xsd</xsl:attribute>
			<xsl:apply-templates select="ms:identificationInfo"/>

			<xsl:for-each select="//ms:languageInfo[generate-id()=generate-id(key('languageName',.)[1])]">
				<dc:language xsi:type="olac:language">
					<xsl:attribute name="olac:code">
					<xsl:apply-templates select="./ms:languageId"/>
					</xsl:attribute>
					<xsl:value-of select="./ms:languageName"/>
					<xsl:if test="ms:languageVarietyInfo"><xsl:text> </xsl:text><xsl:value-of select="./ms:languageVarietyInfo/ms:languageVarietyName"/>
					</xsl:if>
				</dc:language>
			</xsl:for-each>

			<xsl:apply-templates select="ms:resourceComponentType//ms:resourceType"/>
			<xsl:apply-templates select="//ms:mediaType"/>
			
			
			<xsl:for-each select="//ms:licence">
				<dcterms:license>
					<xsl:text>
	</xsl:text><!-- new line -->
					<xsl:value-of select="."/>
					<xsl:if test="../ms:restrictionsOfUse">
	Restrictions of Use: <xsl:for-each select="../ms:restrictionsOfUse"><xsl:value-of select="."/><xsl:if test="not(position()=last())">
							<xsl:text>, </xsl:text></xsl:if>
					</xsl:for-each>
					</xsl:if>
					<xsl:if test="../ms:userNature">
	User Nature: <xsl:for-each select="../ms:userNature"><xsl:value-of select="."/><xsl:if test="not(position()=last())">
							<xsl:text>, </xsl:text></xsl:if>
					</xsl:for-each>
					</xsl:if>
					<xsl:for-each select="../ms:membershipInfo">
						<xsl:text> </xsl:text>
						<xsl:if test="ms:member and ms:membershipInstitution">
	For <xsl:if test="ms:member='False' or ms:member='false'">Non </xsl:if>Members of <xsl:for-each select="ms:membershipInstitution"><xsl:value-of select="."/><xsl:if test="not(position()=last())">
							<xsl:text>, </xsl:text></xsl:if></xsl:for-each>
						<xsl:text> </xsl:text>
						</xsl:if>
					</xsl:for-each>
					<xsl:if test="../ms:fee">
	Fee: <xsl:value-of select="../ms:fee"/>
					</xsl:if>
					<xsl:text>
	</xsl:text><!-- new line -->
				</dcterms:license>
			</xsl:for-each>


			<xsl:choose>
				<xsl:when test="ms:distributionInfo/ms:availabilityStartDate and ms:distributionInfo/ms:availabilityEndDate">
					<dcterms:available><xsl:value-of select="substring(ms:distributionInfo/ms:availabilityStartDate, 1, 4)"/>-<xsl:value-of select="substring(ms:distributionInfo/ms:availabilityEndDate, 1, 4)"/></dcterms:available>
				</xsl:when>
				<xsl:when test="ms:distributionInfo/ms:availabilityStartDate">
					<dcterms:available><xsl:value-of select="ms:distributionInfo/ms:availabilityStartDate"/></dcterms:available>
				</xsl:when>
				<xsl:when test="ms:distributionInfo/ms:availabilityEndDate">
					<dcterms:available><xsl:value-of select="ms:distributionInfo/ms:availabilityEndDate"/></dcterms:available>
				</xsl:when>
			</xsl:choose>

			<xsl:if test="ms:distributionInfo/ms:iprHolder">
				<dcterms:rightsHolder>IPR Holder:<xsl:if test="ms:distributionInfo/ms:iprHolder/ms:personInfo">
					<xsl:text> </xsl:text>
					<xsl:value-of select="ms:distributionInfo/ms:iprHolder/ms:personInfo/ms:givenName"/>
					<xsl:text> </xsl:text>
					<xsl:value-of select="ms:distributionInfo/ms:iprHolder/ms:personInfo/ms:surname"/>
					<xsl:text>, </xsl:text>
					<xsl:value-of select="substring-before(ms:distributionInfo/ms:iprHolder/ms:personInfo/ms:communicationInfo/ms:email, '@')"/><xsl:text>[at]</xsl:text><xsl:value-of select="substring-after(ms:distributionInfo/ms:iprHolder/ms:personInfo/ms:communicationInfo/ms:email, '@')"/> 
					<xsl:if test="ms:distributionInfo/ms:iprHolder/ms:personInfo/ms:affiliation">
						<xsl:text>, </xsl:text>
						<xsl:value-of select="ms:distributionInfo/ms:iprHolder/ms:personInfo/ms:affiliation/ms:organizationName"/>
					</xsl:if>
					<xsl:if test="ms:distributionInfo/ms:iprHolder/ms:organizationInfo">
						<xsl:text>,</xsl:text>
					</xsl:if>
				</xsl:if>
					<xsl:text> </xsl:text><xsl:value-of select="ms:distributionInfo/ms:iprHolder/ms:organizationInfo/ms:organizationName"/>
				</dcterms:rightsHolder>
			</xsl:if>

			<xsl:if test="ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder">
				<dcterms:rightsHolder>Distribution Rights Holder:<xsl:if test="ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:personInfo">
					<xsl:text> </xsl:text>
					<xsl:value-of select="ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:personInfo/ms:givenName"/> 
					<xsl:value-of select="ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:personInfo/ms:surname"/>
					<xsl:text>, </xsl:text>
					<xsl:value-of select="substring-before(ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:personInfo/ms:communicationInfo/ms:email, '@')"/><xsl:text>[at]</xsl:text><xsl:value-of select="substring-after(ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:personInfo/ms:communicationInfo/ms:email, '@')"/> 
					<xsl:if test="ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:personInfo/ms:affiliation">
						<xsl:text>, </xsl:text>
						<xsl:value-of select="ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:personInfo/ms:affiliation/ms:organizationName"/>
					</xsl:if>
					<xsl:if test="ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:organizationInfo">
						<xsl:text>,</xsl:text>
					</xsl:if>
				</xsl:if> 
					<xsl:text> </xsl:text><xsl:value-of select="ms:distributionInfo/ms:licenceInfo/ms:distributionRightsHolder/ms:organizationInfo/ms:organizationName"/>
				</dcterms:rightsHolder>
			</xsl:if>

			<xsl:apply-templates select="//ms:relationInfo/ms:relatedResource/ms:targetResourceNameURI"/>

			<xsl:if test="ms:resourceDocumentationInfo/ms:documentation">
				<dcterms:bibliographicCitation>
					<xsl:choose>
						<xsl:when test="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo">
							<xsl:if test="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:author">
								<xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:author"/>, </xsl:if> <xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:title"/>
							<xsl:if test="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:url">, <xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:url"/></xsl:if>
							<xsl:if test="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:journal">. In: <xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:journal"/></xsl:if>
							<xsl:if test="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:volume">
								<xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:volume"/></xsl:if>
							<xsl:if test="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:pages">, pp.<xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:pages"/></xsl:if>
							<xsl:if test="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:conference">, <xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:conference"/></xsl:if>
							<xsl:if test="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:year">, <xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentInfo/ms:year"/></xsl:if>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="ms:resourceDocumentationInfo/ms:documentation/ms:documentUnstructured"/>
						</xsl:otherwise>
					</xsl:choose>
				</dcterms:bibliographicCitation>
			</xsl:if>

			<xsl:for-each select="//ms:originalSource/ms:targetResourceNameURI">
				<dc:source><xsl:value-of select="(.)"/></dc:source>
			</xsl:for-each>

			<xsl:if test="//ms:geographicCoverage">
				<dcterms:spatial>
				<xsl:attribute name="xsi:type">dcterms:ISO3166</xsl:attribute>
					<xsl:for-each select="//ms:geographicCoverage">
						<xsl:value-of select="."/>
						<xsl:if test="not(position()=last())">
							<xsl:text>, </xsl:text>
					  	</xsl:if>
					</xsl:for-each>
				</dcterms:spatial>
			</xsl:if>

			<xsl:if test="//ms:timeCoverage">
				<dcterms:temporal>
					<xsl:for-each select="//ms:timeCoverage">
						<xsl:value-of select="."/>
						<xsl:if test="not(position()=last())">
							<xsl:text>, </xsl:text>
					  	</xsl:if>
					</xsl:for-each>
				</dcterms:temporal>
			</xsl:if>


			<xsl:if test="ms:resourceComponentType//ms:mimeType">
				<dc:format>
					<xsl:for-each select="//ms:resourceComponentType//ms:mimeType[generate-id()=generate-id(key('mimeType',.)[1])]">
						<xsl:value-of select="."/>
						<xsl:if test="not(position()=last())">
							<xsl:text>, </xsl:text>
					  	</xsl:if>
					</xsl:for-each>
				</dc:format>
			</xsl:if>

			<xsl:if test="//ms:sizeInfo">
				<dcterms:extent>
					<xsl:for-each select="//ms:sizeInfo[generate-id()=generate-id(key('size',.)[1])]">
						<xsl:value-of select="concat(ms:size, ' ', ms:sizeUnit)"/>
						<xsl:if test="not(position()=last())">
							<xsl:text>, </xsl:text>
					  	</xsl:if>
					</xsl:for-each>
				</dcterms:extent>
			</xsl:if>

			<xsl:apply-templates select="ms:distributionInfo/ms:licenceInfo/ms:distributionAccessMedium"/>


			<xsl:choose>
				<xsl:when test="ms:resourceCreationInfo/ms:creationStartDate and ms:resourceCreationInfo/ms:creationEndDate">
					<dcterms:created><xsl:value-of select="substring(ms:resourceCreationInfo/ms:creationStartDate, 1, 4)"/>-<xsl:value-of select="substring(ms:resourceCreationInfo/ms:creationEndDate, 1, 4)"/></dcterms:created>
				</xsl:when>
				<xsl:when test="ms:resourceCreationInfo/ms:creationStartDate">
					<dcterms:created><xsl:value-of select="ms:resourceCreationInfo/ms:creationStartDate"/></dcterms:created>
				</xsl:when>
				<xsl:when test="ms:resourceCreationInfo/ms:creationEndDate">
					<dcterms:created><xsl:value-of select="ms:resourceCreationInfo/ms:creationEndDate"/></dcterms:created>
				</xsl:when>
			</xsl:choose>

			<xsl:if test="ms:resourceCreationInfo/ms:resourceCreator">
				<dc:creator>
					<xsl:for-each select="ms:resourceCreationInfo/ms:resourceCreator">
						<xsl:if test="ms:personInfo">
							<xsl:value-of select="concat(ms:personInfo/ms:givenName, ' ', ms:personInfo/ms:surname)"/>
							<xsl:text>, </xsl:text><xsl:value-of select="substring-before(ms:personInfo/ms:communicationInfo/ms:email, '@')"/><xsl:text>[at]</xsl:text><xsl:value-of select="substring-after(ms:personInfo/ms:communicationInfo/ms:email, '@')"/>
							<xsl:if test="ms:personInfo/ms:affiliation"><xsl:text>, </xsl:text><xsl:value-of select="ms:personInfo/ms:affiliation/ms:organizationName"/></xsl:if>
						</xsl:if>
						<xsl:if test="ms:organizationInfo">
							<xsl:value-of select="ms:organizationInfo/ms:organizationName"/>
						</xsl:if>
						<xsl:if test="not(position()=last())">
							<xsl:text>,
</xsl:text><!-- new line -->
					  	</xsl:if>
					</xsl:for-each>
				</dc:creator>
			</xsl:if>

			<xsl:for-each select="//ms:annotationInfo/ms:annotator">
				<xsl:choose>
					<xsl:when test="ms:personInfo">
						<dc:contributor xsi:type="olac:role" olac:code="annotator"><xsl:value-of select="ms:personInfo/ms:givenName"/><xsl:text> </xsl:text><xsl:value-of select="ms:personInfo/ms:surname"/>
						<xsl:if test="//ms:affiliation">
							<xsl:text>, </xsl:text><xsl:value-of select="ms:personInfo/ms:affiliation/ms:organizationName"/>
						</xsl:if>
						</dc:contributor>
					</xsl:when>
					<xsl:otherwise>
						<dc:contributor xsi:type="olac:role" olac:code="annotator">
						<xsl:if test="//ms:departmentName">
							<xsl:value-of select="ms:organizationInfo/ms:departmentName"/><xsl:text>, </xsl:text>
						</xsl:if>
						<xsl:value-of select="ms:organizationInfo/ms:organizationName"/></dc:contributor>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:for-each>

			<xsl:for-each select="//ms:contactPerson">
				<dc:contributor xsi:type="olac:role" olac:code="depositor"><xsl:value-of select="ms:givenName"/><xsl:text> </xsl:text><xsl:value-of select="ms:surname"/>
				<xsl:text>, </xsl:text><xsl:value-of select="substring-before(ms:communicationInfo/ms:email, '@')"/><xsl:text>[at]</xsl:text><xsl:value-of select="substring-after(ms:communicationInfo/ms:email, '@')"/>
				<xsl:if test="ms:affiliation">
					<xsl:text>, </xsl:text><xsl:value-of select="ms:affiliation/ms:organizationName"/>
				</xsl:if>
				</dc:contributor>
			</xsl:for-each>

		</olac:olac>
	</xsl:template>

</xsl:stylesheet>
