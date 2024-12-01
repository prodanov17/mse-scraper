package com.example.mseapi.service;

import com.example.mseapi.model.Company;
import com.example.mseapi.repository.CompanyRepository;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CompanyService {
    @Autowired
    private CompanyRepository repository;

    public List<Company> getAllCompanies(){
        return this.repository.findAll();
    }
}
