package com.example.mseapi.service;

import com.example.mseapi.dto.CompanyDTO;
import com.example.mseapi.dto.CompanyPredictionsDTO;
import com.example.mseapi.dto.StockDataDTO;
import com.example.mseapi.model.Company;
import org.springframework.data.domain.Pageable;

import java.time.LocalDate;
import java.util.List;

public interface CompanyService {
    List<CompanyDTO> getAllCompanies();
    CompanyDTO getCompanyById(String key);

    StockDataDTO getCompanyStockData(String key, LocalDate startDate, LocalDate endDate, Pageable pageable);
}
