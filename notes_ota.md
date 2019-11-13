# Verschillen tussen de destinations: geldt meestal voor zowel de sitemap als de hotels rates

- Amsterdam:
    - No rate limit
    - Fixed message for (non)breakfast and (non)refundable
    - No user agent check

- London:
    - Rate limit: combo van (destination - ip address - user_agent_category) mag 2 requests / seconde doen. Middleware moet worden toegevoegd om 429 te retryen. Indien reached: 429
    - Variabele breakfast / refundable messages
    - De rates pagina is opgebouwd uit een table ipv div elements, maar ziet er ongeveer hetzelfde uit. De html is broken: een aantal closing </tr> elements te veel, en de hotel info bevat een hidden element waardoor Scrapy niet goed kan parsen. Gebruik BeautifulSoup.

- Paris:
    - Rate limit: combo van (destination - ip address - user_agent_category) mag 2 requests / seconde doen. Middleware moet worden toegevoegd om 429 te retryen. Indien reached: 429
    - Variabele breakfast / refundable messages
    - User agent check: laat enkel user_agent_category toe van hieronder. Defaul user agent is `Scrapy/v....`, hiervoor moeten ze middleware toevoegen om een random UA te pakken. Indien niet: 403

- Brussel:
    - Rate limit: combo van (destination - ip address - user_agent_category) mag 2 requests / seconde doen. Middleware moet worden toegevoegd om 429 te retryen. Indien reached: 429
    - Variabele breakfast / refundable messages
    - User agent check: laat enkel user_agent_category toe van hieronder. Defaul user agent is `Scrapy/v....`, hiervoor moeten ze middleware toevoegen om een random UA te pakken. Indien niet: 403
    - Enkel op de rates pagina: als je doorklikt vanop de search pagina, wordt er een cookie gezet `controlid=<base64(href-path-van-de-link)>`. Cookie kan in de start_requests worden toegevoegd, moet in de settings enabled worden want staat default uit. Indien niet toegevoegd: 400


### user_agent_category: Toegelaten user agents: in de UA van de request worden de volgende strings gezocht (representeren recente versies van grote browsers):

```go
var chrome = []string{"Chrome/76", "Chrome/77", "Chrome/78"}
var firefox = []string{"Firefox/68", "Firefox/69", "Firefox/70"}
var safari = []string{"Safari/603", "Safari/604", "Safari/605"}
var ie = []string{"Trident/7"}
var edge = []string{"Edg/42", "Edg/43", "Edg/44"}
```

Als een gevonden wordt, is de user_agent_category voor de rate limiting de string die gevonden werd.

### Breakfast / Nonrefundable messages:

#### Voor Amsterdam:

```go
	basicrefundableDescription := "Refundable: Yes"
    basicnonrefundableDescription := "Refundable: No"

	basicBreakfastDescription := "Breakfast included: Yes"
	basicNoBreakfastDescription := "Breakfast included: No"
```

#### Voor anderen, telkens een van de volgende strings (deze op index (hotel_id % len(array))):

```go
	refundableDescriptions := []string{
		"Refundable",
		"Free cancellation",
		"Can be cancelled free of charge",
	}
	nonRefundableDescriptions := []string{
		"Non-Refundable",
		"No Free cancellation",
		"Can not be cancelled free of charge",
		"Cancellation incurs a fee",
    }

	breakfastDescriptions := []string{
		"Included free breakfast",
		"With breakfast",
		"All meals are inclusive",
	}
	nobreakfastDescriptions := []string{
		"Does not include free breakfast",
		"No free breakfast included",
		"No breakfast",
		"Breakfast at additional cost",
	}
```


