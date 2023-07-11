# MLDeploy
## Einführung
*MLDeploy* dient als Umgebung für die Integration von ML-Modellen in produktionstechnischen Anwendungsfällen. Es deckt die Funktionalitäten ab, die für den Einsatz eines trainierten Modells im Produktivbetrieb benötigt werden und unterstützt eine Auswahl verschiedener, in der Produktionstechnik verbreiteter Kommunikationsstandards wie z.B. *OPCUA*, *gRPC*, *MQTT*, etc. Ferner ist die Möglichkeit einer einfachen, anwendungsfallspezisfischen Visualisierung und das Erstellen von Alerts teil des Funktionsumfangs von *MLDeploy*.


## Architektur im Beispiel mit einem generischen Processor


![](abstract_concept.png "MLDeploy Structure")


Das Beispiel (Beispiel einfügen) zeigt die Implementierung des ML-Deploy Konzeptes mit einem simulierten Datenstrom und einem zugehörigen ML-Modell. </br> Eine Anpassung auf einen eigenen Anwendungsfall kann mittels des Processor Templates aus diesem Branch abgedeckt werden. Die Infrastrukturkomponenten werden dabei im einfachsten Falle durch das Vornehmen von Einstellungen in den Konfigurationsdateien auf den Anwendungsfall angepasst.

- *Raw Data*

    Bezeichnet die Datenquelle, die anwendugsfallspezifisch ist.

- *Data Adapter*

    Zum Einsatz kommt hier das Tool *Telegraf*, das über verschiedene Input-Plugins Daten aufzeichnen kann. 
    
    Vorgefertigte *input-plugins* existieren für bekannte Standards wie z.B. *OPC UA* und *MQTT*. Die Entwicklung eigener Plugins ist ebenfalls möglich.  

    Gleichermaßen existieren vorgefertigte *output-plugins* wie z.B. für *influx*. Ein output-plugin für den in ML-Deploy genutzten message broker *rabbitmq* ist eine Eigenentwicklung.

- *RabbitMQ* 

    RabbitMQ wird als broker genutzt und verteilt Daten zwischen den Systemkomponenten. Im Zuge der Anpassung des ML-Deploy Frameworks auf den eignen Anwendungsfall wird hier i.d.R. keine Veränderung notwendig.

- *InfluxDB*

    Die open-source Zeitreihendatenbank von *InfluxData* speichert Rohdaten, Features und Modell-Output ab und stellt diese Daten für nachgelagerte Anwendungen langfristig zu Verfügung.
    
    Das *Telegraf* output plugin *influxdb* schreibt Daten in die Datenbank. Nachgelagerte Anwendungen wie z.B. *Grafana* können Daten von der *InfluxDB* anfordern.

- **Processor Template**

    Der generische [Processor](https://hub.autolern.org/wbk/MLDeploy/-/tree/template_example/components/processor/app) bzw. das Processor Template ist das Herzstück der anwendungsfallspezifischen Applikation. Durch Nutzung des Templates können beliebige logische Funktionen, wie die Datenvorverarbeitung und ein ML-Modell in das ML-Deploy System integriert werden. Zur kommunikationstechnischen Anbindung innerhalb des Systems ist lediglich die Angabe des Exchange auf dem message broker notwendig, auf welche geschrieben bzw. von welcher gelesen werden soll.

- *Grafana*

    Zur Visualisierung sowie als Beispiel für eine Anwendung, die ML-Output konsumiert, wird Grafana eingesetzt. Rohdaten. Features und ML-Output können visualisiert werden, ferner ist eine (E-Mail)Benachrichtigung möglich, wenn ML-Output bestimmte Werte annimmt oder unter-/überschreitet.


