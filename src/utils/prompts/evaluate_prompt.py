def setup_evaluation_prompt(original_code: str, updated_code: str, issue_description: str) -> str:
    """
    Constructs a prompt for evaluating the updated code and returns a string that can be used as an input for a model.

    :param original_code: The original code before the update.
    :param updated_code: The updated code after addressing the task.
    :param issue_description: A description of the task or issue addressed in the update.
    :return: A prompt string for evaluation.
    """
    prompt = f"""
    Let me provide you with the original and updated versions of a Java class
    after addressing a specific sonarqube issue.
    
    I need you to evaluate the updated class and determine if it has been correctly updated.
    Especially pay attention to whether or not the updated class has no missing or incorrect parts.
    
    Please review both versions and the issue description to determine if the update is complete and accurate.

    Original Java Class:
    {original_code}

    Updated Java Class:
    {updated_code}

    Issue Description:
    {issue_description}

    I need the response in this format:
    ```json
    {{
        "correctly_updated_class": boolean  // Boolean, whether the updated class has no missing or incorrect parts.
    }}
    ```
    
    """.strip()
    
    return prompt


if __name__ == "__main__":
    # Example usage:
    original_java_class = """
    package com.pairlearning.expensetracker.resources;

    import com.pairlearning.expensetracker.domain.Transaction;
    import com.pairlearning.expensetracker.services.TransactionService;
    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.http.HttpStatus;
    import org.springframework.http.ResponseEntity;
    import org.springframework.web.bind.annotation.*;

    import javax.servlet.http.HttpServletRequest;
    import java.util.HashMap;
    import java.util.List;
    import java.util.Map;

    @RestController
    @RequestMapping("/api/categories/{categoryId}/transactions")
    public class TransactionResource {

        @Autowired
        TransactionService transactionService;

        @GetMapping("")
        public ResponseEntity<List<Transaction>> getAllTransactions(HttpServletRequest request,
                                                                    @PathVariable("categoryId") Integer categoryId) {
            int userId = (Integer) request.getAttribute("userId");
            List<Transaction> transactions = transactionService.fetchAllTransactions(userId, categoryId);
            return new ResponseEntity<>(transactions, HttpStatus.OK);
        }

        @GetMapping("/{transactionId}")
        public ResponseEntity<Transaction> getTransactionById(HttpServletRequest request,
                                                            @PathVariable("categoryId") Integer categoryId,
                                                            @PathVariable("transactionId") Integer transactionId) {
            int userId = (Integer) request.getAttribute("userId");
            Transaction transaction = transactionService.fetchTransactionById(userId, categoryId, transactionId);
            return new ResponseEntity<>(transaction, HttpStatus.OK);
        }

        @PostMapping("")
        public ResponseEntity<Transaction> addTransaction(HttpServletRequest request,
                                                        @PathVariable("categoryId") Integer categoryId,
                                                        @RequestBody Map<String, Object> transactionMap) {
            int userId = (Integer) request.getAttribute("userId");
            Double amount = Double.valueOf(transactionMap.get("amount").toString());
            String note = (String) transactionMap.get("note");
            Long transactionDate = (Long) transactionMap.get("transactionDate");
            Transaction transaction = transactionService.addTransaction(userId, categoryId, amount, note, transactionDate);
            return new ResponseEntity<>(transaction, HttpStatus.CREATED);
        }

        @PutMapping("/{transactionId}")
        public ResponseEntity<Map<String, Boolean>> updateTransaction(HttpServletRequest request,
                                                                    @PathVariable("categoryId") Integer categoryId,
                                                                    @PathVariable("transactionId") Integer transactionId,
                                                                    @RequestBody Transaction transaction) {
            int userId = (Integer) request.getAttribute("userId");
            transactionService.updateTransaction(userId, categoryId, transactionId, transaction);
            Map<String, Boolean> map = new HashMap<>();
            map.put("success", true);
            return new ResponseEntity<>(map, HttpStatus.OK);
        }

        @DeleteMapping("/{transactionId}")
        public ResponseEntity<Map<String, Boolean>> deleteTransaction(HttpServletRequest request,
                                                                    @PathVariable("categoryId") Integer categoryId,
                                                                    @PathVariable("transactionId") Integer transactionId) {
            int userId = (Integer) request.getAttribute("userId");
            transactionService.removeTransaction(userId, categoryId, transactionId);
            Map<String, Boolean> map = new HashMap<>();
            map.put("success", true);
            return new ResponseEntity<>(map, HttpStatus.OK);
        }
    }
    """
    updated_java_class = """
    package com.pairlearning.expensetracker.resources;\n\nimport com.pairlearning.expensetracker.domain.Transaction;\nimport com.pairlearning.expensetracker.services.TransactionService;\nimport org.springframework.beans.factory.annotation.Autowired;\nimport org.springframework.http.HttpStatus;\nimport org.springframework.http.ResponseEntity;\nimport org.springframework.web.bind.annotation.*;\n\nimport javax.servlet.http.HttpServletRequest;\nimport java.util.HashMap;\nimport java.util.List;\nimport java.util.Map;\n\n@RestController\n@RequestMapping(\"/api/categories/{categoryId}/transactions\")\npublic class TransactionResource {\n\n    private static final String USER_ID = \"userId\"; // Added constant for \"userId\"\n\n    @Autowired\n    TransactionService transactionService;\n\n    @GetMapping(\"\")\n    public ResponseEntity<List<Transaction>> getAllTransactions(HttpServletRequest request,\n                                                                @PathVariable(\"categoryId\") Integer categoryId) {\n        int userId = (Integer) request.getAttribute(USER_ID); // Replaced \"userId\" with constant\n        List<Transaction> transactions = transactionService.fetchAllTransactions(userId, categoryId);\n        return new ResponseEntity<>(transactions, HttpStatus.OK);\n    }\n\n    @GetMapping(\"/{transactionId}\")\n    public ResponseEntity<Transaction> getTransactionById(HttpServletRequest request,\n                                                          @PathVariable(\"categoryId\") Integer categoryId,\n                                                          @PathVariable(\"transactionId\") Integer transactionId) {\n        int userId = (Integer) request.getAttribute(USER_ID); // Replaced \"userId\" with constant\n        Transaction transaction = transactionService.fetchTransactionById(userId, categoryId, transactionId);\n        return new ResponseEntity<>(transaction, HttpStatus.OK);\n    }\n\n    @PostMapping(\"\")\n    public ResponseEntity<Transaction> addTransaction(HttpServletRequest request,\n                                                      @PathVariable(\"categoryId\") Integer categoryId,\n                                                      @RequestBody Map<String, Object> transactionMap) {\n        int userId = (Integer) request.getAttribute(USER_ID); // Replaced \"userId\" with constant\n        Double amount = Double.valueOf(transactionMap.get(\"amount\").toString());\n        String note = (String) transactionMap.get(\"note\");\n        Long transactionDate = (Long) transactionMap.get(\"transactionDate\");\n        Transaction transaction = transactionService.addTransaction(userId, categoryId, amount, note, transactionDate);\n        return new ResponseEntity<>(transaction, HttpStatus.CREATED);\n    }\n}
    """
    task_description = "Define a constant instead of duplicating this literal 'userId' 5 times."

    # Get the evaluation prompt.
    evaluation_prompt = setup_evaluation_prompt(original_java_class, updated_java_class, task_description)
    print(evaluation_prompt)
