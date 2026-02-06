# Reverse engineered TipToi API

## Config / Firmware

**Request**:

```
GET /api/v2/config/de_DE/WIN HTTP/1.1
Host: ttapiv2.ravensburger.com
Accept: */*
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsidGlwdG9pIl0sInNjb3BlIjpbInJlYWQiLCJ3cml0ZSJdLCJleHAiOjE3NzAzNzk1NjcsImF1dGhvcml0aWVzIjpbIlJPTEVfQ0xJRU5UIl0sImp0aSI6IjU0NDE1MzFlLTUwNTEtNGI3MC04MDZkLTY0NTM1NzUxZmJlZiIsImNsaWVudF9pZCI6InRpcHRvaS1tYW5hZ2VyLXYyIn0.jvQpiQJp577NTMBbiOkyBIKSt_OYIBi4fLuKJBOQAX69U7S1DwQBeilx40MsTUDNcDRagfYGmUSqPxn4ahhJ4MRtLxUjxoz932p3oR9mvI5-gUkgL03KwNNKj0ShQ2z0AJY1YlUmJJdp-DokzkLbe20X-ad-fqctxtUFEaQ6kxv-G6fAk2sOEkTQf9Gg4z37s6l2XtRFk7YfwhEuvvPHg-qTzEV45IMZQtiuDb9FESZF5Fu44zFcxmpBm-3sK_tCAlsoF4J9x47OSxq4wWdvkSgqCYg0pp0jBXfFKe3qsiLJNjdzM22LShgwf3jlU74b6NnkLodEsQE1XE0TS9vkew
User-Agent: tiptoiManager/5.2
X-Unity-Version: 2021.3.30f1
Connection: keep-alive
```

**Response**:

```
HTTP/2 200 OK
Date: Fri, 06 Feb 2026 11:40:32 GMT
Content-Type: application/json;charset=UTF-8
Server: cloudflare
X-Xss-Protection: 1; mode=block
X-Xss-Protection: 0
Strict-Transport-Security: max-age=31536000; includeSubdomains;
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
X-Content-Type-Options: nosniff
Cache-Control: public, max-age=600
Pragma: no-cache
Expires: Fri, 06 Feb 2026 11:50:32 GMT
X-Frame-Options: DENY
Last-Modified: Fri, 06 Feb 2026 11:30:55 GMT
Cf-Cache-Status: HIT
Age: 568
Vary: accept-encoding
Tdm-Reservation: 1
Cf-Ray: 9c9a5f8f3e67bbf6-ZRH
Alt-Svc: h3=":443"; ma=86400

{
  "catalogModifiedAt":"2026-02-06T11:30:35.200Z",
  "minManagerVersion":"5.0.2",
  "manager":{
    "version":"5.2",
    "url":"https://cdn.ravensburger.de/db/Installer/5.2/tiptoi_Manager_Installer.exe",
    "modifiedAt":"2024-04-09T08:35:14Z"
  },
  "firmware":[
    {
      "penGeneration":"REV1",
      "version":"136",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/136/REV1/update.upd",
      "checksum":"28F7854A",
      "modifiedAt":"2020-07-23T12:15:08Z",
      "fileName":"update.upd"
    },
    {
      "penGeneration":"REV2",
      "version":"38",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/38/REV2/Update3202.upd",
      "checksum":"39EC05ED",
      "modifiedAt":"2020-07-23T12:14:13Z",
      "fileName":"Update3202.upd"
    },
    {
      "penGeneration":"REV3",
      "version":"38",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/38/REV3/update3202MT.upd",
      "checksum":"3A04DD92",
      "modifiedAt":"2018-08-01T08:33:39Z",
      "fileName":"update3202MT.upd"
    },
    {
      "penGeneration":"REV4",
      "version":"43",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/43/REV4/Update3203L.upd",
      "checksum":"5BD66E66",
      "modifiedAt":"2019-04-04T11:43:05Z",
      "fileName":"Update3203L.upd"
    },
    {
      "penGeneration":"REV5",
      "version":"43",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/43/REV5/Update3203L.upd",
      "checksum":"5BD66E66",
      "modifiedAt":"2019-04-04T11:48:01Z",
      "fileName":"Update3203L.upd"
    },
    {
      "penGeneration":"REV6",
      "version":"7",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/7/REV6/Update3203L_eMMC.upd",
      "checksum":"5754FCF2",
      "modifiedAt":"2018-08-01T08:42:53Z",
      "fileName":"Update3203L_eMMC.upd"
    },
    {
      "penGeneration":"REV7",
      "version":"29",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/29/REV7/Update4N.upd",
      "checksum":"5878A383",
      "modifiedAt":"2018-08-14T15:08:35Z",
      "fileName":"Update4N.upd"
    },
    {
      "penGeneration":"REV8",
      "version":"7",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/7/REV8/Update4E.upd",
      "checksum":"47C0C9B6",
      "modifiedAt":"2018-08-01T08:51:09Z",
      "fileName":"Update4E.upd"
    },
    {
      "penGeneration":"REV11",
      "version":"7",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/7/REV11/Update3203L.upd",
      "checksum":"5754FCF2",
      "modifiedAt":"2021-01-13T13:48:04Z",
      "fileName":"Update3203L.upd"
    },
    {
      "penGeneration":"REV12",
      "version":"27",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/27/REV12/Update6E.upd",
      "checksum":"6F9A80B4",
      "modifiedAt":"2020-12-09T09:28:40Z",
      "fileName":"Update6E.upd"
    },
    {
      "penGeneration":"REV13",
      "version":"13",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/13/REV13/Update5E.upd",
      "checksum":"547AB1F0",
      "modifiedAt":"2022-07-12T08:54:44Z",
      "fileName":"Update5E.upd"
    },
    {
      "penGeneration":"REV14",
      "version":"26",
      "url":"https://cdn.ravensburger.de/db/Firmware-Files/de/26/REV14/Update7GE.upd",
      "checksum":"51551D1D",
      "modifiedAt":"2024-06-25T07:49:38Z",
      "fileName":"Update7GE.upd"
    }
  ],
  "ttApiVersion":"2.5-SNAPSHOT"
}
```

## Catalog

**Request**:

```
GET /api/v2/catalog/de_DE HTTP/2
Host: ttapiv2.ravensburger.com
Accept: */*
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsidGlwdG9pIl0sInNjb3BlIjpbInJlYWQiLCJ3cml0ZSJdLCJleHAiOjE3NzAzNzk1NjcsImF1dGhvcml0aWVzIjpbIlJPTEVfQ0xJRU5UIl0sImp0aSI6IjU0NDE1MzFlLTUwNTEtNGI3MC04MDZkLTY0NTM1NzUxZmJlZiIsImNsaWVudF9pZCI6InRpcHRvaS1tYW5hZ2VyLXYyIn0.jvQpiQJp577NTMBbiOkyBIKSt_OYIBi4fLuKJBOQAX69U7S1DwQBeilx40MsTUDNcDRagfYGmUSqPxn4ahhJ4MRtLxUjxoz932p3oR9mvI5-gUkgL03KwNNKj0ShQ2z0AJY1YlUmJJdp-DokzkLbe20X-ad-fqctxtUFEaQ6kxv-G6fAk2sOEkTQf9Gg4z37s6l2XtRFk7YfwhEuvvPHg-qTzEV45IMZQtiuDb9FESZF5Fu44zFcxmpBm-3sK_tCAlsoF4J9x47OSxq4wWdvkSgqCYg0pp0jBXfFKe3qsiLJNjdzM22LShgwf3jlU74b6NnkLodEsQE1XE0TS9vkew
User-Agent: tiptoiManager/5.2
X-Unity-Version: 2021.3.30f1
```

**Response**:

```
{
  "modifiedAt":"2026-02-06T11:32:35.215Z",
  "products":[
    {
      "id":"00171",
      "name":"Tiere der Welt",
      "categories":[
        "Spiele"
      ],
      "ageFrom":4,
      "ageTo":8,
      "shortDescription":"",
      "description":"Ob Säugetiere, Fische, Vögel oder Insekten - in diesem Deduktionsspiel lernen die Kinder 44 Tiere aus allen Erdteilen kennen. tiptoi stellt Fragen und beschreibt das gesuchte Tier: Findest du ein Tier, das in Europa lebt? Das gesuchte Tier kann fliegen. Über mehrere Runden wird ein Tier anhand seiner Eigenschaften beschrieben. Dabei gibt es Tipps, die auf mehrere Tiere zutreffen. Wer das gesuchte Tier errät, bekommt Punkte. Mit viel Spaß erwerben die Kinder Sachwissen rund um die Tiere der Welt.",
      "images":[
        {
          "tags":[
            "search"
          ],
          "url":"https://ravensburger.cloud/images/produktseiten/70/00171.jpg",
          "modifiedAt":"2000-01-01T00:00:00Z",
          "fileName":"00171.jpg",
          "dimension":"70"
        },
        {
          "tags":[
            "thumb"
          ],
          "url":"https://ravensburger.cloud/images/produktseiten/210/00171.jpg",
          "modifiedAt":"2000-01-01T00:00:00Z",
          "fileName":"00171.jpg",
          "dimension":"210"
        },
        {
          "tags":[
            "detail"
          ],
          "url":"https://ravensburger.cloud/images/produktseiten/360/00171.jpg",
          "modifiedAt":"2000-01-01T00:00:00Z",
          "fileName":"00171.jpg",
          "dimension":"360"
        }
      ],
      "shopUrl":"https://www.ravensburger.de/00171/product.html",
      "gameFiles":[
        {
          "id":"270",
          "url":"https://ravensburger.cloud/rvwebsite/rvDE/db/applications/Tiere_der_Welt.gme",
          "version":"20230726",
          "modifiedAt":"2023-08-21T13:44:42Z",
          "fileName":"Tiere_der_Welt.gme"
        }
      ],
      "releaseDate":"2023-09-01T00:00:00Z"
    },
    {
      "id":"00523",
      "name":"Puzzeln, Entdecken, Erleben: Beim Kinderarzt",
      "categories":[
        "Puzzle"
      ],
      "ageFrom":5,
      "ageTo":8,
      "shortDescription":"",
      "description":"Immer wieder neuer Spielverlauf \nSpannende, interaktive Situationen in der Praxis\nSachwissen zu Körper und Gesundheit, Schulung der Motorik und Konzentration\n\nIn der Kinderarztpraxis ist ganz schön was los: Ein aufgeschlagenes Knie muss versorgt werden, ein Allergietest steht an und ein Patient wartet auf seine Impfung. Wenn das Puzzle fertig zusammengesetzt ist, wird durch tiptoi® der Praxisalltag erlebbar gemacht. Der Spieler hilft mit, die Patienten zu versorgen und bekommt dabei einen Einblick in die Aufgaben in einer Kinderarztpraxis.",
      "images":[
        {
          "tags":[
            "search"
          ],
          "url":"https://ravensburger.cloud/images/produktseiten/70/00523.jpg",
          "modifiedAt":"2000-01-01T00:00:00Z",
          "fileName":"00523.jpg",
          "dimension":"70"
        },
        {
          "tags":[
            "thumb"
          ],
          "url":"https://ravensburger.cloud/images/produktseiten/210/00523.jpg",
          "modifiedAt":"2000-01-01T00:00:00Z",
          "fileName":"00523.jpg",
          "dimension":"210"
        },
        {
          "tags":[
            "detail"
          ],
          "url":"https://ravensburger.cloud/images/produktseiten/360/00523.jpg",
          "modifiedAt":"2000-01-01T00:00:00Z",
          "fileName":"00523.jpg",
          "dimension":"360"
        }
      ],
      "shopUrl":"https://www.ravensburger.de/00523/product.html",
      "gameFiles":[
        {
          "id":"28",
          "url":"https://ravensburger.cloud/rvwebsite/rvDE/db/applications/Puzzle%20Kinderarzt.gme",
          "version":"20141017",
          "modifiedAt":"2018-08-22T13:20:41Z",
          "fileName":"Puzzle Kinderarzt.gme"
        }
      ],
      "releaseDate":"2012-01-01T00:00:00Z"
    },

...

],
  "bestsellers":[
  ],
  "recommended":[
    "00801",
    "00830",
    "00837",
    "41810",
    "43514"
  ],
  "marketingTiles":[
    {
      "text":"Kennst du diese Tiergeräusche?",
      "image":"https://ravensburger.cloud/images/produktseiten/360/49303.jpg",
      "type":"ttmanager",
      "target":"ttmanager://link/product?id=49303"
    },
    {
      "text":"Mein erstes Bild-Wörterbuch Deutsch-Englisch",
      "image":"https://ravensburger.cloud/images/produktseiten/360/49297.jpg",
      "type":"ttmanager",
      "target":"ttmanager://link/product?id=49297"
    },
    {
      "text":"Kira Katze und die Sache mit dem Streit",
      "image":"https://ravensburger.cloud/images/produktseiten/360/49299.jpg",
      "type":"ttmanager",
      "target":"ttmanager://link/product?id=49299"
    },
    {
      "text":"Team SMART ermittelt: Diebstahl im Tier-Express",
      "image":"https://ravensburger.cloud/images/produktseiten/360/00226.jpg",
      "type":"ttmanager",
      "target":"ttmanager://link/product?id=00226"
    }
  ]
}
```

## GME download

**Request**:

```
GET /rvwebsite/rvDE/db/applications/Tiergeraeusche.gme HTTP/1.1
Host: ravensburger.cloud
Accept: */*
Accept-Encoding: gzip, deflate, br
User-Agent: tiptoiManager/5.2
X-Unity-Version: 2021.3.30f1
Connection: keep-alive
```

**Response**:

```
HTTP/2 200 OK
Date: Fri, 06 Feb 2026 11:42:05 GMT
Content-Type: application/octet-stream
Content-Length: 12546820
Server: cloudflare
Tdm-Reservation: 1
Last-Modified: Fri, 01 Aug 2025 11:33:47 GMT
Etag: "bf7304-63b4c2198f6d0"
X-Xss-Protection: 0
Content-Security-Policy: frame-ancestors 'self' www.ravensburger.de www.ravensburger.fr www.ravensburger.org www.ravensburger.us www.ravensburger.ie www.ravensburger.it www.ravensburger.be www.ravensburger.es www.ravensburger.nl www.ravensburger.pl www.brio.se;
Cf-Cache-Status: HIT
Age: 153499
Expires: Fri, 13 Feb 2026 11:42:05 GMT
Cache-Control: public, max-age=604800
Accept-Ranges: bytes
Speculation-Rules: "/cdn-cgi/speculation"
Vary: accept-encoding
Cf-Ray: 9c9a61d19a2c8bbd-ZRH
Alt-Svc: h3=":443"; ma=86400
```
