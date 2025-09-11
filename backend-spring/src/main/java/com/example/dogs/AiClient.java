package com.example.dogs;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import java.util.Map;

@Component
public class AiClient {
  private final WebClient webClient;
  public AiClient(@Value("${ai.base-url}") String baseUrl, WebClient.Builder builder){
    this.webClient = builder.baseUrl(baseUrl).build();
  }

  public Mono<Map> classify(byte[] bytes, String filename, int topK){
    ByteArrayResource res = new ByteArrayResource(bytes){ @Override public String getFilename(){ return filename; }};
    MultiValueMap<String, Object> form = new LinkedMultiValueMap<>();
    form.add("file", res);
    return webClient.post()
      .uri(uriBuilder -> uriBuilder.path("/v1/classify").queryParam("top_k", topK).build())
      .contentType(MediaType.MULTIPART_FORM_DATA)
      .body(BodyInserters.fromMultipartData(form))
      .retrieve().bodyToMono(Map.class);
  }

  public Mono<Map> searchSimilar(byte[] bytes, String filename, int topK){
    ByteArrayResource res = new ByteArrayResource(bytes){ @Override public String getFilename(){ return filename; }};
    MultiValueMap<String, Object> form = new LinkedMultiValueMap<>();
    form.add("file", res);
    return webClient.post()
      .uri(uriBuilder -> uriBuilder.path("/v1/search/similar").queryParam("top_k", topK).build())
      .contentType(MediaType.MULTIPART_FORM_DATA)
      .body(BodyInserters.fromMultipartData(form))
      .retrieve().bodyToMono(Map.class);
  }

  public Mono<Map> adoptionCopy(Map<String, Object> body){
    return webClient.post().uri("/v1/generate/adoption-copy")
      .contentType(MediaType.APPLICATION_JSON)
      .bodyValue(body)
      .retrieve().bodyToMono(Map.class);
  }
}
