package com.example.mseapi.controller;

import com.example.mseapi.dto.CompanyDTO;
import com.example.mseapi.dto.StockDataDTO;
import com.example.mseapi.model.Company;
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
    private CompanyServiceImpl service;

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
}
