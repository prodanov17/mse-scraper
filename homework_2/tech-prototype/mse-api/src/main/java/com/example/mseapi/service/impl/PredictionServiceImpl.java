package com.example.mseapi.service.impl;

import com.example.mseapi.dto.CompanyPredictionsDTO;
import com.example.mseapi.service.PredictionService;
import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

@Service
public class PredictionServiceImpl implements PredictionService {
    private static final String PREDICTION_API_BASE_URL = "http://prediction:5000/predict";

    private final RestTemplate restTemplate;
    public PredictionServiceImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Override
    @Cacheable("predictions")
    public CompanyPredictionsDTO getCompanyPrediction(String key) {
        String url = UriComponentsBuilder.fromHttpUrl(PREDICTION_API_BASE_URL)
                .queryParam("symbol", key)
                .toUriString();

        try {
            // Fetch response as JSON
            JsonNode response = restTemplate.getForObject(url, JsonNode.class);

            // Map response to DTO
            CompanyPredictionsDTO dto = new CompanyPredictionsDTO();
            dto.setKey(response.get("symbol").asText());
            dto.setPrediction(response.get("predicted_price").asDouble());
            return dto;
        } catch (Exception e) {
            throw new RuntimeException("Failed to fetch prediction for symbol: " + key, e);
        }
    }
}
