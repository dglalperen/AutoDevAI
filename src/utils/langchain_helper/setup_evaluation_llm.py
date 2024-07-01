import json
import os
from openai import OpenAI


def evaluate_llm_response(prompt: str, model: str = "gpt-4o"):
    """
    Sends an evaluation prompt to the OpenAI model and returns the response.

    :param prompt: The prompt to send to the model for evaluation.
    :param model: The model version to use for the evaluation.
    :return: The response from the model.
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant tasked with evaluating an updated Java class. Verify that the issue described has been resolved correctly and that there are no truncations or incorrect modifications in the updated class. Return a JSON object with a boolean value indicating whether the updated class is correctly updated.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    # print("EVALUATION RESPONSE")
    # print(60 * "-")
    response_text = response.choices[0].message.content if response.choices else None
    # print(response_text)
    # print(60 * "-")

    return response_text


if __name__ == "__main__":
    original_java_class = """
    package de.hsruhrwest.malteweiss.exercisegenerator.exercises.logic.booltabletonf;
    import de.hsruhrwest.malteweiss.exercisegenerator.exercises.AbstractExerciseGenerator;
    import de.hsruhrwest.malteweiss.exercisegenerator.model.ExerciseTO;
    import lombok.AllArgsConstructor;
    import lombok.Builder;
    import lombok.Data;
    import lombok.NoArgsConstructor;
    import lombok.extern.log4j.Log4j2;
    import org.apache.commons.math3.random.RandomDataGenerator;
    import org.thymeleaf.context.Context;
    import org.thymeleaf.spring6.SpringTemplateEngine;

    import java.util.ArrayList;
    import java.util.HashMap;
    import java.util.List;
    import java.util.Map;
    import java.util.stream.Collectors;
    import java.util.stream.IntStream;

    @Log4j2
    public abstract class AbstractBoolTableToNFBase extends AbstractExerciseGenerator {
        @Builder
        @Data
        @NoArgsConstructor
        @AllArgsConstructor
        public static class Model {
            private int dimension;
            private Map<Integer, Integer> function;
        }

        public AbstractBoolTableToNFBase(String name) {
            super(Model.class, name);
        }

        @Override
        public ExerciseTO createExercise(SpringTemplateEngine templateEngine) {
            var randomDataGenerator = new RandomDataGenerator();

            // Create model
            int dimension = 3;
            int maxValue = (int) Math.pow(2, dimension) - 1;

            Map<Integer, Integer> function = new HashMap<>();
            for(int i = 0; i <= maxValue; i++) {
                function.put(i, randomDataGenerator.nextInt(0, 1));
            }

            // Create question text
            Context ctx = new Context();

            // Truth table
            List<String> truthTableRows = new ArrayList<>();

            truthTableRows.add("<tr>"
                    + IntStream.range(0, dimension).mapToObj(i -> String.format("<td>%c</td>", 'A' + i)).collect(Collectors.joining())
                    + "<td>" + getFunctionDefinitionString(dimension) + "</td>"
                    + "</tr>");

            for(int value = 0; value <= maxValue; value++) {
                StringBuilder builder = new StringBuilder();
                for(int i = 0; i < dimension; i++) {
                    boolean bit = (value & (1 << (dimension - i - 1))) != 0;
                    builder.append(String.format("<td>%s</td>", bit ? "w" : "f"));
                }
                builder.append(String.format("<td>%s</td>", function.get(value) != 0 ? "w" : "f"));
                truthTableRows.add("<tr>" + builder.toString() + "</tr>");
            }

            ctx.setVariable("truthTableRows", truthTableRows);
            ctx.setVariable("taskText", getTemplateTaskText());
            var question = processQuestionTemplate(templateEngine, ctx);

            Model model = Model.builder()
                .dimension(dimension)
                .function(function)
                .build();

            return new ExerciseTO(question, model);
        }

        @Override
        public long getNumberOfVariants() {
            return (long) Math.pow(2, 8);
        }

        @Override
        public String createSolution(SpringTemplateEngine templateEngine, Object modelObject) {
            Model model = (Model) modelObject;

            int dimension = model.getDimension();
            Map<Integer, Integer> function = model.getFunction();

            // Additional hint
            String additionalHint = null;
            if(function.values().stream().allMatch(v -> v.equals(0))) {
                // Special case: All values are 0
                additionalHint = "Die Funktion ist unerfüllbar/widerspruchsvoll.";
            }
            else if(function.values().stream().allMatch(v -> v.equals(1))) {
                // Special case: All values are 1
                additionalHint = "Die Funktion ist allgemeingültig.";
            }

            Context ctx = new Context();
            ctx.setVariable("formulaRows", getFormulaRows(function, dimension));
            ctx.setVariable("answerText", getTemplateAnswerText());
            ctx.setVariable("additionalHint", additionalHint);

            return processSolutionTemplate(templateEngine, ctx);
        }

        /**
        * Generates all rows for a formula table.
        * @param function function
        * @param dimension dimension of function
        * @return formular rows as strings
        */
        private List<String> getFormulaRows(Map<Integer, Integer> function, int dimension) {
            List<String> formulaRows = new ArrayList<>();

            int maxValue = (int) Math.pow(2, dimension) - 1;

            // Special case: All values are 0
            if(function.values().stream().allMatch(v -> v.equals(0))) {
                formulaRows.add("<tr>"
                        + "<td>" + getFunctionDefinitionString(dimension) + "</td>"
                        + "<td>=</td>"
                        + "<td>0</td>"
                        + "</tr>");
            }
            // Special case: All values are 1
            else if(function.values().stream().allMatch(v -> v.equals(1))) {
                formulaRows.add("<tr>"
                        + "<td>" + getFunctionDefinitionString(dimension) + "</td>"
                        + "<td>=</td>"
                        + "<td>1</td>"
                        + "</tr>");
            }
            // Regular case
            else {
                boolean first = true;
                for (int value = 0; value <= maxValue; value++) {
                    if (isRelevantRow(function.get(value) != 0)) {
                        StringBuilder builder = new StringBuilder();
                        if (first) {
                            builder.append(String.format("<td>%s =</td><td></td>", getFunctionDefinitionString(dimension)));
                            first = false;
                        } else {
                            builder.append(String.format("<td></td><td>%s</td>", getSolutionOuterOperatorHtml()));
                        }
                        builder.append("<td>(</td>");
                        for (int i = 0; i < dimension; i++) {
                            boolean bit = (value & (1 << (dimension - i - 1))) != 0;
                            builder.append(String.format("<td>%s%c</td>", getParameterPrefixForLetter(bit), 'A' + i));
                            if (i < dimension - 1) {
                                builder.append(String.format("<td>%s</td>", getSolutionInnerOperatorHtml()));
                            }
                        }
                        builder.append("<td>)</td>");
                        formulaRows.add(builder.toString());
                    }
                }
            }
            return formulaRows;
        }

        /**
        * Creates string for function definition: f(A,B,C,...)
        * @param dimension dimension of function
        * @return definition string
        */
        private String getFunctionDefinitionString(int dimension) {
            return String.format("f(%s)", IntStream.range(0, dimension).mapToObj(j -> String.format("%c", 'A' + j)).collect(Collectors.joining(", ")));
        }

        @Override
        protected String getTemplateName() {
            return "BoolTableToNF";
        }

        /**
        * @param truthTableValue function value of a row in the truth table
        * @return whether row in function f(A,B,C,...) is relevant for final formula
        */
        protected abstract boolean isRelevantRow(boolean truthTableValue);

        /**
        * @param parameterValue value that is set to a specific parameter
        * @return the prefix for a parameter A, B, C, ... depending on the value that is assigned to this parameter
        */
        protected abstract String getParameterPrefixForLetter(boolean parameterValue);

        /**
        * @return template task text
        */
        protected abstract String getSolutionInnerOperatorHtml();

        /**
        * @return template task text
        */
        protected abstract String getSolutionOuterOperatorHtml();

        /**
        * @return template task text
        */
        protected abstract String getTemplateTaskText();

        /**
        * @return template answer text
        */
        protected abstract String getTemplateAnswerText();
    }
    """

    updated_java_class = """
    package de.hsruhrwest.malteweiss.exercisegenerator.exercises.logic.booltabletonf;\n\nimport de.hsruhrwest.malteweiss.exercisegenerator.exercises.AbstractExerciseGenerator;\nimport de.hsruhrwest.malteweiss.exercisegenerator.model.ExerciseTO;\nimport lombok.AllArgsConstructor;\nimport lombok.Builder;\nimport lombok.Data;\nimport lombok.NoArgsConstructor;\nimport lombok.extern.log4j.Log4j2;\nimport org.apache.commons.math3.random.RandomDataGenerator;\nimport org.thymeleaf.context.Context;\nimport org.thymeleaf.spring6.SpringTemplateEngine;\n\nimport java.util.ArrayList;\nimport java.util.HashMap;\nimport java.util.List;\nimport java.util.Map;\nimport java.util.stream.Collectors;\nimport java.util.stream.IntStream;\n\n@Log4j2\npublic abstract class AbstractBoolTableToNFBase extends AbstractExerciseGenerator {\n    private static final String TD_TAG_END = \"</td>\";\n\n    @Builder\n    @Data\n    @NoArgsConstructor\n    @AllArgsConstructor\n    public static class Model {\n        private int dimension;\n        private Map<Integer, Integer> function;\n    }\n\n    public AbstractBoolTableToNFBase(String name) {\n        super(Model.class, name);\n    }\n\n    @Override\n    public ExerciseTO createExercise(SpringTemplateEngine templateEngine) {\n        var randomDataGenerator = new RandomDataGenerator();\n\n        // Create model\n        int dimension = 3;\n        int maxValue = (int) Math.pow(2, dimension) - 1;\n\n        Map<Integer, Integer> function = new HashMap<>();\n        for(int i = 0; i <= maxValue; i++) {\n            function.put(i, randomDataGenerator.nextInt(0, 1));\n        }\n\n        // Create question text\n        Context ctx = new Context();\n\n        // Truth table\n        List<String> truthTableRows = new ArrayList<>();\n\n        truthTableRows.add(\"<tr>\"\n                + IntStream.range(0, dimension).mapToObj(i -> String.format(\"<td>%c\", 'A' + i)).collect(Collectors.joining())\n                + TD_TAG_END + \"<td>\" + getFunctionDefinitionString(dimension) + TD_TAG_END\n                + \"</tr>\");\n\n        for(int value = 0; value <= maxValue; value++) {\n            StringBuilder builder = new StringBuilder();\n            for(int i = 0; i < dimension; i++) {\n                boolean bit = (value & (1 << (dimension - i - 1))) != 0;\n                builder.append(String.format(\"<td>%s\", bit ? \"w\" : \"f\"));\n                builder.append(TD_TAG_END);\n            }\n            builder.append(String.format(\"<td>%s\", function.get(value) != 0 ? \"w\" : \"f\"));\n            builder.append(TD_TAG_END);\n            truthTableRows.add(\"<tr>\" + builder.toString() + \"</tr>\");\n        }\n\n        ctx.setVariable(\"truthTableRows\", truthTableRows);\n        ctx.setVariable(\"taskText\", getTemplateTaskText());\n        var question = processQuestionTemplate(templateEngine, ctx);\n\n        Model model = Model.builder()\n            .dimension(dimension)\n            .function(function)\n            .build();\n\n        return new ExerciseTO(question, model);\n    }\n\n    @Override\n    public long getNumberOfVariants() {\n        return (long) Math.pow(2, 8);\n    }\n\n    @Override\n    public String createSolution(SpringTemplateEngine templateEngine, Object modelObject) {\n        Model model = (Model) modelObject;\n\n        int dimension = model.getDimension();\n        Map<Integer, Integer> function = model.getFunction();\n\n        // Additional hint\n        String additionalHint = null;\n        if(function.values().stream().allMatch(v -> v.equals(0))) {\n            // Special case: All values are 0\n            additionalHint = \"Die Funktion ist unerfüllbar/widerspruchsvoll.\";\n        }\n        else if(function.values().stream().allMatch(v -> v.equals(1))) {\n            // Special case: All values are 1\n            additionalHint = \"Die Funktion ist allgemeingültig.\";\n        }\n\n        Context ctx = new Context();\n        ctx.setVariable(\"formulaRows\", getFormulaRows(function, dimension));\n        ctx.setVariable(\"answerText\", getTemplateAnswerText());\n        ctx.setVariable(\"additionalHint\", additionalHint);\n\n        return processSolutionTemplate(templateEngine, ctx);\n    }\n\n    private List<String> getFormulaRows(Map<Integer, Integer> function, int dimension) {\n        List<String> formulaRows = new ArrayList<>();\n\n        int maxValue = (int) Math.pow(2, dimension) - 1;\n\n        // Special case: All values are 0\n        if(function.values().stream().allMatch(v -> v.equals(0))) {\n            formulaRows.add(\"<tr>\"\n                    + \"<td>\" + getFunctionDefinitionString(dimension) + TD_TAG_END\n                    + \"<td>=</td>\"\n                    + \"<td>0</td>\"\n                    + \"</tr>\");\n        }\n        // Special case: All values are 1\n        else if(function.values().stream().allMatch(v -> v.equals(1))) {\n            formulaRows.add(\"<tr>\"\n                    + \"<td>\" + getFunctionDefinitionString(dimension) + TD_TAG_END\n                    + \"<td>=</td>\"\n                    + \"<td>1</td>\"\n                    + \"</tr>\");\n        }\n        // Regular case\n        else {\n            boolean first = true;\n            for (int value = 0; value <= maxValue; value++) {\n                if (isRelevantRow(function.get(value) != 0)) {\n                    StringBuilder builder = new StringBuilder();\n                    if (first) {\n                        builder.append(String.format(\"<td>%s =</td><td></td>\", getFunctionDefinitionString(dimension)));\n                        first = false;\n                    } else {\n                        builder.append(String.format(\"<td></td><td>%s</td>\", getSolutionOuterOperatorHtml()));\n                    }\n                    builder.append(\"<td>(</td>\");\n                    for (int i = 0; i < dimension; i++) {\n                        boolean bit = (value & (1 << (dimension - i - 1))) != 0;\n                        builder.append(String.format(\"<td>%s%c\", getParameterPrefixForLetter(bit), 'A' + i));\n                        builder.append(TD_TAG_END);\n                        if (i < dimension - 1) {\n                            builder.append(String.format(\"<td>%s\", getSolutionInnerOperatorHtml()));\n                            builder.append(TD_TAG_END);\n                        }\n                    }\n                    builder.append(\"<td>)</td>\");\n                    formulaRows.add(\"<tr>\" + builder.toString() + \"</tr>\");\n                }\n            }\n        }\n        return formulaRows;\n    }\n\n    @Override\n    protected String getTemplateName() {\n        return \"BoolTableToNF\";\n    }\n\n    protected abstract boolean isRelevantRow(boolean truthTableValue);\n\n    protected abstract String getParameterPrefixForLetter(boolean parameterValue);\n\n    protected abstract String getSolutionInnerOperatorHtml();\n\n    protected abstract String getSolutionOuterOperatorHtml();\n\n    protected abstract String getTemplateTaskText();\n\n    protected abstract String getTemplateAnswerText();\n}\n
    """

    issue_description = (
        "Define a constant instead of duplicating this literal '</td>' 3 times."
    )

    prompt = f"""
        Let me provide you with the original and updated versions of a Java class after addressing a specific SonarQube issue.

        The task is to evaluate whether the updated class correctly implements the necessary changes to address the issue and whether it maintains all other aspects of the original class without any omissions or incorrect modifications.

        Review both the original and updated class code in light of the issue description. Confirm that the issue is resolved correctly in the updated class and that no original functionality or structure is missing or altered incorrectly.

        Original Java Class:
        {original_java_class}

        Updated Java Class:
        {updated_java_class}

        Issue Description:
        {issue_description}

        Please return the response in this JSON format:

        ```json
        {{
            "correctly_updated_class": boolean  // Boolean, whether the updated class is correctly updated addressing the issue without any missing or incorrect parts.
        }}
    """

    evaluate_llm_response(prompt)
