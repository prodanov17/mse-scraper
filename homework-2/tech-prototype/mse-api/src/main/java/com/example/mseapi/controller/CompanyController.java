package com.example.mseapi.controller;

import com.example.mseapi.model.Company;
import com.example.mseapi.service.CompanyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/companies")
public class CompanyController {
    @Autowired
    private CompanyService service;

    @GetMapping
    public List<Company> getAllCompanies(){
        return this.service.getAllCompanies();
    }
}
