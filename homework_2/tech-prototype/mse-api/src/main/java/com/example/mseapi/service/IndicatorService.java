package com.example.mseapi.service;

import com.example.mseapi.dto.IndicatorDTO;

import java.util.List;

public interface IndicatorService {
    List<IndicatorDTO> getIndicators(String key, String indicator);
}
