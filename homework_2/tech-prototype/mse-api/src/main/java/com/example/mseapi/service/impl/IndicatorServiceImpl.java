package com.example.mseapi.service.impl;

import com.example.mseapi.dto.IndicatorDTO;
import com.example.mseapi.service.IndicatorService;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Service
public class IndicatorServiceImpl implements IndicatorService {
    private static final String INDICATOR_URL = "http://indicators:5000/{key}/indicators/{indicator}";

    @Autowired
    private RestTemplate restTemplate;
    @Override
    @Cacheable("indicators")
    public List<IndicatorDTO> getIndicators(String key, String indicator) {
        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<String> response = restTemplate.getForEntity(INDICATOR_URL, String.class, key.toUpperCase(), indicator);

        if (response.getStatusCode().is2xxSuccessful()) {
            try {
                // Parse the JSON response into a List of IndicatorDTO
                ObjectMapper objectMapper = new ObjectMapper();
                return objectMapper.readValue(
                        response.getBody(),
                        new TypeReference<List<IndicatorDTO>>() {}
                );
            } catch (Exception e) {
                throw new RuntimeException("Failed to parse the response", e);
            }
        } else {
            throw new RuntimeException("Failed to fetch indicator data for key: " + key);
        }
    }
}
