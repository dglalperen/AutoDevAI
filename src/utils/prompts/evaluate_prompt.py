def setup_evaluation_prompt(
    original_code: str, updated_code: str, issue_description: str
) -> str:
    """
    Constructs a prompt for evaluating the updated code and returns a string that can be used as an input for a model.

    Parameters:
    - original_code: The original Java code before the update.
    - updated_code: The Java code after attempting to address the issue.
    - issue_description: A description of the SonarQube issue addressed in the update.

    Returns:
    - A prompt string structured to guide the evaluation of the updated code.
    """
    prompt = f"""
        Below are the original and updated versions of a Java class that was modified to address a specific SonarQube issue described below. Your task is to evaluate the updated class to determine if it correctly implements the necessary changes without introducing errors or omitting necessary parts of the original class.

        **Issue Description:** {issue_description}

        **Original Java Class:**
        {original_code}

        **Updated Java Class:**
        {updated_code}

        Evaluate the updated class to ensure:
        1. The specific issue described above is addressed correctly.
        2. All original functionality and structure are maintained unless directly related to the fix.
        3. There are no new errors or issues introduced in the updated class.

        Please return your evaluation in this JSON format:
        ```json
        {{
            "correctly_updated_class": true/false  // Indicate 'true' if the updated class is correctly updated or 'false' otherwise.
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
    task_description = (
        "Define a constant instead of duplicating this literal 'userId' 5 times."
    )

    # Get the evaluation prompt.
    evaluation_prompt = setup_evaluation_prompt(
        original_java_class, updated_java_class, task_description
    )
    # print(evaluation_prompt)
