package com.example.dogs;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;
import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/v1")
public class DogController {
  private final AiClient ai;
  public DogController(AiClient ai){ this.ai = ai; }

  @PostMapping(value = "/dogs/classify", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
  public Mono<Map> classify(@RequestPart("file") MultipartFile file, @RequestParam(defaultValue="5") int top_k) throws IOException {
    return ai.classify(file.getBytes(), file.getOriginalFilename(), top_k);
  }

  @PostMapping(value = "/dogs/search-similar", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
  public Mono<Map> similar(@RequestPart("file") MultipartFile file, @RequestParam(defaultValue="8") int top_k) throws IOException {
    return ai.searchSimilar(file.getBytes(), file.getOriginalFilename(), top_k);
  }

  @PostMapping("/text/adoption-copy")
  public Mono<Map> copy(@RequestBody Map<String, Object> body){
    return ai.adoptionCopy(body);
  }
}
