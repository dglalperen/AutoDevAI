from openai import OpenAI
import os

# Assuming OPENAI_API_KEY is set in your environment variables
api_key = os.getenv("OPENAI_API_KEY")


def generate_fix_for_issue(java_class_content, issue_description):
    client = OpenAI(api_key=api_key)

    # Crafting a prompt based on the example run
    prompt = f"""
    Let's fix a SonarQube issue in a Java project. The issue is as follows: "{issue_description}". Below is the Java class with the issue:

    {java_class_content}

    Define a constant for duplicated literals as suggested and return the updated Java class in a JSON format:

    {{
        "updated_java_class": "Your fixed Java class here"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
                   You are an expert Java developer that corrects
                   SonarQube issues. Fix the issue based on the provided
                   description. You always return your response in this json format:
                    ```json
                    {
                        "updated_java_class": string  // The updated Java class code, encapsulated in a JSON object.
                    }
                   """,
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        n=1,
        response_format={"type": "json_object"},
    )

    # Assuming the response is well-structured and follows the expected format
    try:
        updated_java_class = response.choices[0].message
        print("Successfully retrieved the updated Java class.")
        return updated_java_class
    except Exception as e:
        print(f"Error processing the API response: {e}")
        return None


# Simulate the scenario with a specific class content and issue description
java_class_content = """package com.pairlearning.expensetracker.resources;

import com.pairlearning.expensetracker.domain.Category;
import com.pairlearning.expensetracker.services.CategoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/categories")
public class CategoryResource {

    @Autowired
    CategoryService categoryService;

    @GetMapping("")
    public ResponseEntity<List<Category>> getAllCategories(HttpServletRequest request) {
        int userId = (Integer) request.getAttribute("userId");
        List<Category> categories = categoryService.fetchAllCategories(userId);
        return new ResponseEntity<>(categories, HttpStatus.OK);
    }

    @GetMapping("/{categoryId}")
    public ResponseEntity<Category> getCategoryById(HttpServletRequest request,
                                                    @PathVariable("categoryId") Integer categoryId) {
        int userId = (Integer) request.getAttribute("userId");
        Category category = categoryService.fetchCategoryById(userId, categoryId);
        return new ResponseEntity<>(category, HttpStatus.OK);
    }

    @PostMapping("")
    public ResponseEntity<Category> addCategory(HttpServletRequest request,
                                                @RequestBody Map<String, Object> categoryMap) {
        int userId = (Integer) request.getAttribute("userId");
        String title = (String) categoryMap.get("title");
        String description = (String) categoryMap.get("description");
        Category category = categoryService.addCategory(userId, title, description);
        return new ResponseEntity<>(category, HttpStatus.CREATED);
    }

    @PutMapping("/{categoryId}")
    public ResponseEntity<Map<String, Boolean>> updateCategory(HttpServletRequest request,
                                                               @PathVariable("categoryId") Integer categoryId,
                                                               @RequestBody Category category) {
        int userId = (Integer) request.getAttribute("userId");
        categoryService.updateCategory(userId, categoryId, category);
        Map<String, Boolean> map = new HashMap<>();
        map.put("success", true);
        return new ResponseEntity<>(map, HttpStatus.OK);
    }

    @DeleteMapping("/{categoryId}")
    public ResponseEntity<Map<String, Boolean>> deleteCategory(HttpServletRequest request,
                                                               @PathVariable("categoryId") Integer categoryId) {
        int userId = (Integer) request.getAttribute("userId");
        categoryService.removeCategoryWithAllTransactions(userId, categoryId);
        Map<String, Boolean> map = new HashMap<>();
        map.put("success", true);
        return new ResponseEntity<>(map, HttpStatus.OK);
    }
}"""
issue_description = """
this is the actual issue description:
    "Define a constant instead of duplicating this literal "userId" 5 times."
"""

updated_class_code = generate_fix_for_issue(java_class_content, issue_description)

if updated_class_code:
    print("Updated Java Class Code:", updated_class_code)
else:
    print("Failed to generate an updated Java class.")
