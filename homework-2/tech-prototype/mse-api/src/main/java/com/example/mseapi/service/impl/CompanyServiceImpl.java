package com.example.mseapi.service.impl;

import com.example.mseapi.dto.CompanyDTO;
import com.example.mseapi.dto.StockDataDTO;
import com.example.mseapi.model.Company;
import com.example.mseapi.model.StockData;
import com.example.mseapi.repository.CompanyRepository;
import com.example.mseapi.repository.StockDataRepository;
import com.example.mseapi.service.CompanyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class CompanyServiceImpl implements CompanyService {
    @Autowired
    private CompanyRepository repository;
    @Autowired
    private StockDataRepository stockDataRepository;

    public List<CompanyDTO> getAllCompanies() {
        // Fetch all companies
        List<Company> companies = repository.findAll();

        // Fetch latest stock data for all companies
        Map<String, Double[]> stockDataMap = stockDataRepository.findLatestStockDataForAllCompanies()
                .stream()
                .collect(Collectors.toMap(
                        row -> (String) row[0], // companyKey
                        row -> new Double[]{
                                row[1] != null ? (Double) row[1] : 0.0, // price
                                row[2] != null ? (Double) row[2] : 0.0  // priceChange
                        }
                ));

        // Map to CompanyDTO
        return companies.stream()
                .map(c -> {
                    Double[] stockData = stockDataMap.get(c.getCompanyKey());
                    Double price = stockData != null ? stockData[0] : 0.0;
                    Double priceChange = stockData != null ? stockData[1] : 0.0;
                    return new CompanyDTO(c.getName(), c.getCompanyKey(), price, priceChange);
                })
                .toList();
    }


    @Override
    public CompanyDTO getCompanyById(String key) {
        Object[] stockData = this.stockDataRepository.findLatestStockDataForAllCompanies(key);

        Double price = 0.0;
        Double priceChange = 0.0;

        if (stockData != null && stockData.length > 0) {
            Object[] nestedData = (Object[]) stockData[0]; // Extract the nested array/object
            if (nestedData.length >= 3) {
                price = nestedData[1] != null ? (Double) nestedData[1] : 0.0;
                priceChange = nestedData[2] != null ? (Double) nestedData[2] : 0.0;
            }
        }

        Optional<Company> company = this.repository.findById(key);

        if (company.isEmpty()) {
            throw new RuntimeException("Company not found");
        }

        return new CompanyDTO(company.get().getName(), company.get().getCompanyKey(), price, priceChange);
    }


    public StockDataDTO getCompanyStockData(String key, LocalDate startDate, LocalDate endDate, Pageable pageable){
        Optional<Company> company = this.repository.findById(key);

        if(company.isEmpty()) throw new RuntimeException("Not found");

        Page<StockData> stockData = this.stockDataRepository.findByCompanyCompanyKeyAndDateBetween(key, startDate, endDate, pageable);

        StockDataDTO dto = new StockDataDTO();
        dto.setCompanyKey(company.get().getCompanyKey());
        dto.setName(company.get().getName());
        dto.setStockData(stockData);

        return dto;
    }
}
