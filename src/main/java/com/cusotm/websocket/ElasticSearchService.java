package com.cusotm.websocket;

import com.cusotm.websocket.dto.*;
import com.google.gson.Gson;
import com.google.gson.internal.LinkedTreeMap;
import org.springframework.stereotype.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Component
public class ElasticSearchService {


    public static int timeWindowInS = 10;

    public static void main(String[] args) {
        List<MessageDTO> logMessages = new ElasticSearchService().getLogMessages();

        System.out.println(logMessages);

    }

    private final static String URL = "http://localhost:9200/tomcat9-access-logs/_search";

    public List<MessageDTO> getLogMessages() {


//        GET tomcat9-access-logs-2021.01.02/_search
//        {
//          "query": {
//            "range": {
//              "event.ingested": {
//                    "gte" : "2021-01-02T13:19:10.777Z",
//                    "lt" :  "2021-01-02T13:19:52.777Z"
//
//              }
//            }
//          }
//        }
        try {

            EventIngested ingested = new EventIngested();

            Range range = new Range();
            range.eventIngested = ingested;

            Query query = new Query();

            QueryDTO queryDTO = new QueryDTO();
            queryDTO.query = query;


            Gson gson = new Gson();

            HttpClient client = HttpClient.newBuilder()
                    .version(HttpClient.Version.HTTP_1_1)
                    .build();

            String jsonString = gson.toJson(queryDTO);

            jsonString = "{ \"size\":500,  \"query\": {    \"range\": {      \"event.ingested\": {            \"gte\" : \"now-" + timeWindowInS + "s\",            \"lt\" :  \"now\"          }    }  }}";

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(URL))

                    .timeout(Duration.ofMinutes(1))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonString))
                    .build();

            HttpResponse<String> response =
                    client.send(request, HttpResponse.BodyHandlers.ofString());

            System.out.println(response);

            Map<String, Object> map = gson.fromJson(response.body(), Map.class);

            LinkedTreeMap hits = (LinkedTreeMap) map.get("hits");

            ArrayList hits1 = (ArrayList) hits.get("hits");

            List<MessageDTO> logMessages = (List<MessageDTO>) hits1.stream().map(it -> getMessageDTO((LinkedTreeMap) it)).collect(Collectors.toList());

            System.out.println("Number of logMessage found: " + logMessages.size());

            return logMessages;

//         curl -XGET "http://localhost:9200/tomcat9-access-logs-2021.01.02/_search" -H 'Content-Type: application/json' -d'{  "query": {    "range": {      "event.ingested": {            "gte" : "now-30m",            "lt" :  "now"          }    }  }}'        


        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;

    }

    private MessageDTO getMessageDTO(final LinkedTreeMap hit) {
        LinkedTreeMap hit1 = hit;

        String timestamp = (String) ((LinkedTreeMap) hit1.get("_source")).get("@timestamp");

        String message = (String) ((LinkedTreeMap) hit1.get("_source")).get("message");

        return new MessageDTO(message, timestamp);
    }

    private Date toDate(final LocalDateTime imeFrom) {
        return Date.from(imeFrom.atZone(ZoneId.systemDefault()).toInstant());
    }


}
