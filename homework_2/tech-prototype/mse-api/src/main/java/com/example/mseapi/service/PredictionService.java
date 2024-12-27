package com.example.mseapi.service;

import com.example.mseapi.dto.CompanyPredictionsDTO;

public interface PredictionService {
    CompanyPredictionsDTO getCompanyPrediction(String key);

}
