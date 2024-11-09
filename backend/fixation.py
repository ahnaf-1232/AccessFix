import io
import pandas as pd
import asyncio
import os
import time
import glob
import subprocess
import numpy as np
from dotenv import load_dotenv
from LLM_functions import LLMFunctions
from web_scrapper import fetch_and_save_data, save_code_to_path
from file_handler import extract_text_from_pdf, extract_text_from_docx, extract_text_from_html


def run_playwright_test():
    try:
        env = os.environ.copy()
        env['CI'] = '1'  # Set the CI variable

        subprocess.run('npx playwright test', shell=True, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running Playwright test: {e}")


class CleanGPTModels:
    def __init__(self):
        load_dotenv()
        self.gpt_functions = LLMFunctions()

        if not os.path.exists('violationResult.csv'):
            with open('violationResult.csv', 'w') as file:
                file.write('id,impact,tags,description,help,helpUrl,nodeImpact,nodeHtml,nodeTarget,nodeType,message,numViolation\n')

        self.input_df = pd.read_csv('violationResult.csv')

    def add_severity_score(self, df, column_name, insert_index):
        impact_values = {
            'critical': 5,
            'serious': 4,
            'moderate': 3,
            'minor': 2,
            'cosmetic': 1,
        }
        df['impactValue'] = df['impact'].map(impact_values)
        df.insert(insert_index, column_name, df['impactValue'])
        df.drop(columns='impactValue', inplace=True)
        return df

    def calculate_severity_score(self, df, score):
        return df[score].sum()

    def create_corrected_dom_column(self, path):
        print("Correcting DOMs..........")

        if self.input_df.empty:
            print("No violations found; skipping DOM correction.")
            self.final_corrected_dom = None
            return
            
        error_fix_dict = {}

        with open(path, 'r', encoding='utf-8') as text_file:
            dom = text_file.read()

        for index, row in self.input_df.iterrows():
            error = row['nodeHtml']
            fix = self.gpt_functions.get_correction(index)
            error_fix_dict[error] = fix

        dom_corrected = dom
        for error, fix in error_fix_dict.items():
            dom_corrected = dom_corrected.replace(error[3:-3], fix[3:-3])

        self.input_df['DOMCorrected'] = dom_corrected
        self.final_corrected_dom = dom_corrected

        corrected_path = path.replace(".html", "_corrected.html")
        with open(corrected_path, 'w', encoding='utf-8') as corrected_file:
            corrected_file.write(dom_corrected)

        print(f"Final corrected DOM saved to {corrected_path}")


    def remove_files_starting_with(self, pattern):
        files_to_remove = glob.glob(pattern)
        for file_path in files_to_remove:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except OSError as e:
                print(f"Error while removing file '{file_path}': {e}")

    def create_test_script(self, path):   
        print("Creating the violation file...........")

        with open(path, 'r', encoding='utf-8') as text_file:
            dom = text_file.read()

        test_script_path = "./tests/before.spec.ts"
        with open(test_script_path, "w", encoding='utf-8') as f:
            f.write(f"""
                // @ts-check
                const {{ test, expect }} = require('@playwright/test');
                const AxeBuilder = require('@axe-core/playwright').default;
                const fileReader = require('fs');

                function escapeCSV(value) {{
                    if (typeof value === 'string') {{
                        value = value.replace(/"/g, '""');
                        if (value.includes(',') || value.includes('\\n') || value.includes('\\r') || value.includes('"')) {{
                            return `"${{value}}"`;
                        }}
                    }}
                    return value;
                }}

                function violationsToCSV(violations) {{
                    const headers = ['id', 'impact', 'tags', 'description', 'help', 'helpUrl', 'nodeImpact', 'nodeHtml', 'nodeTarget', 'nodeType', 'message', 'numViolation'];
                    let csvContent = headers.join(',') + '\\n';               
                    const totalViolations = violations.length; 

                    violations.forEach(violation => {{
                        violation.nodes.forEach(node => {{
                            const nodeImpacts = ['any', 'all', 'none'];
                            nodeImpacts.forEach(impactType => {{
                                if (node[impactType] && node[impactType].length > 0) {{
                                    node[impactType].forEach(check => {{
                                        const row = [
                                            escapeCSV(violation.id),
                                            escapeCSV(violation.impact),
                                            escapeCSV(violation.tags.join('|')),
                                            escapeCSV(violation.description),
                                            escapeCSV(violation.help),
                                            escapeCSV(violation.helpUrl),
                                            escapeCSV(check.impact || ''),
                                            escapeCSV(node.html),
                                            escapeCSV(node.target.join('|')),
                                            escapeCSV(impactType),
                                            escapeCSV(check.message),
                                            escapeCSV(totalViolations)
                                        ];
                                        csvContent += row.join(',') + '\\n';
                                    }});
                                }}
                            }});
                        }});
                    }});
                    
                    return csvContent;
                }}

                test('accessibility issues', async ({{ page }}) => {{
                    await page.setContent(`{dom}`);
                    const accessibilityScanResults = await new AxeBuilder({{ page }}).analyze();
                    const violations = accessibilityScanResults.violations;

                    // Write CSV data to file
                    fileReader.writeFileSync("violationResult.csv", violationsToCSV(violations));
                    // Write the number of violations to a file
                    fileReader.writeFileSync("num_of_violations.txt", String(violations.length));
                }});
            """)

        # Run the Playwright test script after creation
        run_playwright_test()
        time.sleep(1)


        if os.path.exists('num_of_violations.txt'):
            try:
                os.remove('num_of_violations.txt')
            except PermissionError:
                time.sleep(1)
                os.remove('num_of_violations.txt')        

    def correction_to_violations(self, corrected_dom):
        test_script_path = "./tests/after.spec.ts"
        with open(test_script_path, "w", encoding='utf-8') as f:
            f.write(f"""
            // @ts-check
            const {{ test, expect }} = require('@playwright/test');
            const AxeBuilder = require('@axe-core/playwright').default;
            const fileReader = require('fs');

            test('all violations', async ({{ page }}) => {{
                await page.setContent(`{corrected_dom}`)
                const accessibilityScanResults = await new AxeBuilder({{ page }}).analyze();
                const violations = accessibilityScanResults.violations;

                fileReader.writeFile("num_of_violations.txt", String(violations.length), function(err) {{
                    if (err) console.log(err);
                }});

                for (let i = 0; i < violations.length; i++) {{
                    fileReader.writeFile("data" + i + ".json", JSON.stringify(violations[i]), function(err) {{
                        if (err) console.log(err);
                    }});
                }}
            }});
            """
            
            
            )

        run_playwright_test()
        time.sleep(1)

        length = 0
        if os.path.exists('num_of_violations.txt'):
            with open('num_of_violations.txt', "r") as length_file:
                length = int(length_file.readline().strip())

        new_df = pd.DataFrame()

        if length > 0:
            for i in range(length):
                df_temp = pd.read_json(f"data{i}.json", lines=True)
                df_temp = df_temp.reset_index(drop=True)
                new_df = pd.concat([new_df, df_temp])
            new_df.insert(1, "numViolations", length)
        else:
            df_temp = pd.DataFrame({
                'id': ['None'],
                'impact': ['None'],
                'tags': ['None'],
                'description': ['None'],
                'help': ['None'],
                'helpUrl': ['None'],
                'nodeHtml': ['None'],
                'nodeImpact': ['None'],
                'nodeType': ['None'],
                'message': ['None'],          
                'numViolations': [0]
            })
            df_temp = df_temp.reset_index(drop=True)
            new_df = pd.concat([new_df, df_temp])

        new_df = new_df.reset_index(drop=True)
        self.remove_files_starting_with("data*")

        if os.path.exists('num_of_violations.txt'):
            try:
                os.remove('num_of_violations.txt')
            except PermissionError:
                time.sleep(1)
                os.remove('num_of_violations.txt')

        new_df = self.add_severity_score(new_df, 'finalScore', 3)
        return new_df

    def call_corrections_to_violations(self, url):
        print("Violation result after corrections.....")
        df_corrections = pd.DataFrame()
        dom_corrected = self.input_df.iloc[0]['DOMCorrected']

        df_temp = self.correction_to_violations(dom_corrected)
        df_corrections = pd.concat([df_corrections, df_temp])
        df_corrections.to_csv('correctionViolations.csv', index=False)
        return df_corrections



    def analyze_violations_from_URL(self, url, path):
        fetch_and_save_data(url, path)
        self.create_test_script(path)
        self.input_df = self.add_severity_score(self.input_df, 'initialScore', 5)
        
        print("total # of violations: ", len(self.input_df))

        total_initial_severity_score = self.calculate_severity_score(self.input_df, 'initialScore')
        self.create_corrected_dom_column(path)
        
        dom_corrected = self.input_df.iloc[0]['DOMCorrected']
        result_df = self.correction_to_violations(dom_corrected)
       
        total_final_severity_score = self.calculate_severity_score(result_df, 'finalScore')
        total_improvement = ((1 - (total_final_severity_score / total_initial_severity_score)) * 100)


        print(f"Total initial severity score: {total_initial_severity_score}")
        print(f"Total final severity score: {total_final_severity_score}")
        print(f"Total improvement: {total_improvement}")
        # print(result_df)

        return {
            "total_initial_severity_score": int(total_initial_severity_score) if isinstance(total_initial_severity_score, np.integer) else total_initial_severity_score,
            "total_final_severity_score": int(total_final_severity_score) if isinstance(total_final_severity_score, np.integer) else total_final_severity_score,
            "total_improvement": float(total_improvement) if isinstance(total_improvement, (np.integer, np.floating)) else total_improvement,
            # "result_df": result_df.to_dict()
        }
    

    def analyze_violations_from_code(self, code, path):
        save_code_to_path(code, path)
        self.create_test_script(path)
        self.input_df = self.add_severity_score(self.input_df, 'initialScore', 5)
        
        print("total # of violations: ", len(self.input_df))

        total_initial_severity_score = self.calculate_severity_score(self.input_df, 'initialScore')
        self.create_corrected_dom_column(path)
        
        dom_corrected = self.input_df.iloc[0]['DOMCorrected']
        result_df = self.correction_to_violations(dom_corrected)
       
        total_final_severity_score = self.calculate_severity_score(result_df, 'finalScore')
        total_improvement = ((1 - (total_final_severity_score / total_initial_severity_score)) * 100)


        print(f"Total initial severity score: {total_initial_severity_score}")
        print(f"Total final severity score: {total_final_severity_score}")
        print(f"Total improvement: {total_improvement}")
        # print(result_df)

        return {
            "total_initial_severity_score": int(total_initial_severity_score) if isinstance(total_initial_severity_score, np.integer) else total_initial_severity_score,
            "total_final_severity_score": int(total_final_severity_score) if isinstance(total_final_severity_score, np.integer) else total_final_severity_score,
            "total_improvement": float(total_improvement) if isinstance(total_improvement, (np.integer, np.floating)) else total_improvement,
            # "result_df": result_df.to_dict()
        }


    async def analyze_violations_from_file(self, file, path):
        try:
            # Asynchronously read file content
            file_content = await file.read()

            # Check the file type and extract text accordingly
            if file.filename.endswith(".pdf"):
                code = extract_text_from_pdf(file_content)  # Ensure this function can handle bytes input
            elif file.filename.endswith(".docx"):
                code = extract_text_from_docx(file_content)
            elif file.filename.endswith(".html"):
                code = extract_text_from_html(file_content)
            else:
                raise ValueError("Unsupported file format")

            # Analyze the extracted code
            return self.analyze_violations_from_code(code, path)

        except Exception as e:
            print(f"Error processing file: {e}")
            raise ValueError("Failed to process file content")



def analyzeURL(url: str):
    model = CleanGPTModels()
    path = 'data/input.html'
    return model.analyze_violations_from_URL(url, path)


def analyzeCode(code: str):
    model = CleanGPTModels()
    path = 'data/input.html'
    return model.analyze_violations_from_code(code, path)


def analyzeCodeFromFile(file):
    model = CleanGPTModels()
    path = 'data/input.html'
    return model.analyze_violations_from_file(file, path)
