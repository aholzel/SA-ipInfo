# SA-ipInfo app
Deze app bestaat uit twee delen
1) Een script om de Maxmind IP database (en eventueel andere databases in geval van een abonement) te downloaden
2) Een 5 tal scripts om alle info uit de databases te gebruiken.

# Referenties / Credits
Het update script is gebaseerd op het door Maxmind beschikbaar gestelde update script.
De scripts om (alle) info uit de databases te gebruiken is gebaseerd op de door Ryan Faircloth gemaakt app "SecKit for geolocation with MaxMind" (https://splunkbase.splunk.com/app/3022/)

# Benodigdheden:
- De Splunk app SA-ipInfo
- Een internet connectie naar http://updates.maxmind.com
- Optioneel: Een abonnement bij Maxmind en de daarbij behorende UserID en LicenseKey

# Maxmind database update script

**Probleem:**
De IP-locatie database die standaard met Splunk mee komt wordt standaard slechts geüpdate bij een update van de Splunk Core. Aangezien deze ongeveer een keer in de 2 a 3 maanden een update krijg, en een productie omgeving niet altijd meteen kan worden bijgewerkt ga je achterlopen met de locatie informatie van IP-adressen.
Maxmind (de leverancier van de IP-locatie database) heeft een update script dat gebruikt kan worden om de nieuwste versie van de database te downloaden, dit script is echter geschreven in Perl en maakt gebruik van een aantal modules die standaard niet geïnstalleerd zijn. Daarnaast moet wil je misschien niet altijd het originele bestand overschrijven om een back-up te hebben in geval van problemen.
 
**Oplossing:**
Splunk biedt de mogelijkheid (hoewel niet heel goed/duidelijk beschreven) om de IP 
locatie database handmatig te updaten of om een ander bestand te gebruiken in plaats 
van het standaard bestand. Hierdoor kun je er zelf voor zorgen dat de Splunk omgeving
gebruik maakt van de meest recente versie van de IP-locatie database. 
Om ervoor te zorgen dat er geen extra installatie nodig is van bijvoorbeeld Perl modules is het script van Maxmind herschreven naar Python en maakt het alleen gebruik van standaard modules. Dit om ervoor te zorgen dat het met de door Splunk mee geleverde Python werkt. Daarnaast is er wel voor gezorgd dat het op dezelfde manier gebruikt kan worden als het door Maxmind geleverde script met.

**Script werking/features**
- Maakt gebruik van het door Maxmind gemaakte GeoIP.conf bestand.
- Maakt gebruik van de door Maxmind geleverde update mogelijkheden om te checken of de database geüpdate moet worden.
- Download de database alleen als er een nieuwe versie is.
- Maakte de nieuwste versie meteen beschikbaar voor Splunk
- Logs t.b.v. troubleshooting op 4 levels(Debug/Info/Warning/Error)

# Database info scripts

**Probleem:**
In de databases die Maxmind heeft zitten meer velden dan dat het Splunk iplocation commando terug geeft, ook zit er in Splunk geen mogelijkheid om gebruik te maken van de overige databases die Maxmind heeft. Het Splunk iplocation commando geeft standaard alle de volgende 5 velden terug: City, Country, Region, lat, lon. 

**Oplossing:**
Met de diverse scripts die in deze app zitten komen er (indien alle databases beschikbaar zijn) 21 velden terug (info van de Maxmind site):

| Veld | Beschikbaar in macro | Omschrijving |
| :--- | :--- | :--- |
| accuracy_radius | Alle macro's | The approximate accuracy radius in kilometers around the latitude and longitude for the IP address. This is the radius where we have a 67% confidence that the device using the IP address resides within the circle centered at the latitude and longitude with the provided radius. |
| city | Alle macro's | The name of the city. |
| connection_type | ip_connection_info | The connection type may take the following values| Dialup, Cable/DSL, Corporate, Cellular |
| continent | Alle macro's | Returns the name of the c
| country_iso | | The two-character ISO 3166-1 alpha code for the country. |Continent. |
| country | Alle macro's | The name of the country.|
| domain | ip_domain_info | The second level domain associated with the IP address. This will be something like “example.com” or “example.co.uk”, not “foo.example.com”. |
| is_anonymous_proxy | ip_connection_info | This is true if the IP is an anonymous proxy. See http|//dev.maxmind.com/faq/geoip#anonproxy for further details. |
| is_satellite_provider | ip_connection_info | This is true if the IP address is from a satellite provider that provides service to multiple countries. |
| isp | ip_isp_info | The name of the ISP associated with the IP address. This attribute is only available from the City and Insights web service end points and the GeoIP2 Enterprise database. |
| isp_asn | ip_isp_info | The autonomous system number associated with the IP address. |
| isp_asn_organization | ip_isp_info | The organization associated with the registered autonomous system number for the IP address. |
| isp_ip | ip_isp_info | The IP address used in the lookup |
| lat | Alle macro's | The approximate latitude of the location associated with the IP address. This value is not precise and should not be used to identify a particular address or household. |
| long | Alle macro's | The approximate longitude of the location associated with the IP address. This value is not precise and should not be used to identify a particular address or household. |
| postalcode | ip_location_info | The postal code of the location. Postal codes are not available for all countries. In some countries, this will only contain part of the postal code. |
| registered_country | ip_country_info | The registered country object for the requested IP address. This record represents the country where the ISP has registered a given IP block in and may differ from the user’s country. |
| represented_country | ip_country_info | Object for the country represented by the users of the IP address when that country is different than the country in country. For instance, the country represented by an overseas military base. |
| subdivision | ip_location_info | The name of the subdivision based on the locales list passed to the constructor. |
| subdivision_iso | ip_location_info | The name of the country based on the locales list passed to the constructor. |
| timezone | ip_location_info | The time zone associated with location, as specified by the IANA Time Zone Database, e.g., “America/New_York”. |

**Script werking/features**
- Kan omgaan met de volgende 5 (betaalde) en/of 2 gratis Maxmind databases:
	+ GeoIP2-City.mmdb ($)
	+ GeoIP2-Connection-Type.mmdb ($)
	+ GeoIP2-Country.mmdb ($)
	+ GeoIP2-Domain.mmbd ($)
	+ GeoIP2-ISP.mmdb ($)
	+ GeoIPLite2-City.mmdb
	+ GeoIPLite2-Country.mmdb
- Levert een 6 tal macro's die gebuikt kunnen worden om info op te vragen. Een per database en een om alle info uit alle databases te halen.
- Kan door middel van de "prefix" functionaliteit in een query voor zowel het source ip als het destination ip worden gebruikt zonder dat de informatie elkaar zal "bijten"

**Note:**
De database info scripts gaan ervanuit dat de databases in de "data" directory van de app staan, het update script uit de app plaatst de databases standaard in deze directory, indien er geen gebruik gemaakt wordt van het update script zullen de bestanden daar handmatig moeten worden geplaatst.

**ToDo/Issues**
1. Indien het opgegeven veld geen informatie bevat zal er gebruik worden gemaakt van een tijdelijk ip adres (127.254.254.254) in de macros om te voorkomen dat het script een error terug geeft.
2. Er vind geen validatie plaats van het IP adres voor dat deze door het script verwerkt wordt, het ingeven van een ongeldig IP adres (bijvoorbeeld 999.9.9.9) levert een error op.
3. De limits.conf file moet handmatig worden aangepast voor de gratis of betaalde versie van de Maxmind database. >> Fixed in versie 1.3