package com.example.mseapi.controller;

import com.example.mseapi.dto.*;
import com.example.mseapi.model.Company;
import com.example.mseapi.service.CompanyService;
import com.example.mseapi.service.IndicatorService;
import com.example.mseapi.service.NewsService;
import com.example.mseapi.service.PredictionService;
import com.example.mseapi.service.impl.CompanyServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/companies")
public class CompanyController {
    @Autowired
    private CompanyService service;

    @Autowired
    private PredictionService predictionService;

    @Autowired
    private IndicatorService indicatorService;


    @Autowired
    private NewsService newsService;

    @GetMapping("/{key}/news/sentiment")
    public NewsSentimentDTO getCompanyNewsSentiment(@PathVariable String key) {
        return newsService.getNewsSentiment(key);
    }

    @GetMapping
    public List<CompanyDTO> getAllCompanies(){
        return this.service.getAllCompanies();
    }

    @GetMapping("/{key}/price-history")
    public StockDataDTO getCompanyStockData(
            @PathVariable String key,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate
    ){
        Pageable pageable = PageRequest.of(page, size, Sort.by("date").descending());
        LocalDate start = (startDate != null) ? LocalDate.parse(startDate) : LocalDate.of(1900, 1, 1);
        LocalDate end = (endDate != null) ? LocalDate.parse(endDate) : LocalDate.of(2100, 12, 31);
        return this.service.getCompanyStockData(key.toUpperCase(), start, end, pageable);
    }

    @GetMapping("/{key}")
    public CompanyDTO getCompanyByKey(
            @PathVariable String key
    ){
        return this.service.getCompanyById(key.toUpperCase());
    }

    @GetMapping("/{key}/predict")
    public CompanyPredictionsDTO getCompanyPrediction(@PathVariable String key) {
        return this.predictionService.getCompanyPrediction(key.toUpperCase());
    }

    @GetMapping("/{key}/indicators/{indicator}")
    public List<IndicatorDTO> getCompanyIndicator(@PathVariable String key, @PathVariable String indicator) {
        return this.indicatorService.getIndicators(key.toUpperCase(), indicator);
    }
}
