import pandas as pd
import os
import platform
import time
import glob
import subprocess
import openai
from dotenv import load_dotenv
from ollama_functions import LLMFunctions
from gemma_functions import GemmaFunctions
from gpt_functions import GPTFunctions
from web_scrapper import fetch_and_save_data


def run_playwright_test():
    try:
        # Copy the current environment variables
        env = os.environ.copy()
        env['CI'] = '1'  # Set the CI variable

        if platform.system() == 'Windows':
            # Run the Playwright test on Windows
            subprocess.run('npx playwright test', shell=True, check=True, env=env)
        else:
            # Run the Playwright test on Unix-based systems
            subprocess.run('npx playwright test', shell=True, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running Playwright test: {e}")


class CleanGPTModels:
    def __init__(self):
        load_dotenv()
        self.gpt_functions = LLMFunctions()
        # openai.api_key = os.getenv('OPENAI_API_KEY')

        if not os.path.exists('violationsWithFixedContent.csv'):
            # Create a file with headers or empty content
            with open('violationsWithFixedContent.csv', 'w') as file:
                file.write('id,impact,tags,description,help,helpUrl,nodeImpact,nodeHtml,nodeTarget,nodeType,message,numViolation\n')

        # Now read the file into a DataFrame
        self.input_df = pd.read_csv('violationsWithFixedContent.csv')

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
        error_fix_dict = {}

        with open(path, 'r', encoding='utf-8') as text_file:
            dom = text_file.read()

        for index, row in self.input_df.iterrows():
            error = row['nodeHtml']
            fix = self.gpt_functions.get_correction(index)
            error_fix_dict[error] = fix

        dom_corrected = dom
        for error, fix in error_fix_dict.items():
            dom_corrected = dom_corrected.replace(error[3:-3], fix[3:-3])  # Remove enclosing [[ ]]

        self.input_df['DOMCorrected'] = dom_corrected
        # self.df.to_csv('corrections.csv', index=False)    #kichu bujhi naaaaaaaaa

    def remove_files_starting_with(self, pattern):
        files_to_remove = glob.glob(pattern)
        for file_path in files_to_remove:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except OSError as e:
                print(f"Error while removing file '{file_path}': {e}")

    def create_test_script(self, url, path):   
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
                    fileReader.writeFileSync("violationsWithFixedContent.csv", violationsToCSV(violations));
                    // Write the number of violations to a file
                    fileReader.writeFileSync("num_violations.txt", String(violations.length));
                }});
            """)

        # Run the Playwright test script after creation
        run_playwright_test()
        time.sleep(1)


        if os.path.exists('num_violations.txt'):
            try:
                os.remove('num_violations.txt')
            except PermissionError:
                time.sleep(1)
                os.remove('num_violations.txt')        


    def corrections2violations(self, corrected_dom):
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

                fileReader.writeFile("num_violations2.txt", String(violations.length), function(err) {{
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
        if os.path.exists('num_violations2.txt'):
            with open('num_violations2.txt', "r") as length_file:
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

        if os.path.exists('num_violations2.txt'):
            try:
                os.remove('num_violations2.txt')
            except PermissionError:
                time.sleep(1)
                os.remove('num_violations2.txt')

        new_df = self.add_severity_score(new_df, 'finalScore', 3)
        return new_df

    def call_corrections2violations(self, url):
        print("Violation result after corrections.....")
        df_corrections = pd.DataFrame()
        dom_corrected = self.input_df.iloc[0]['DOMCorrected']
        # print("checking", url)
        df_temp = self.corrections2violations(dom_corrected)
        df_corrections = pd.concat([df_corrections, df_temp])
        df_corrections.to_csv('correctionViolations.csv', index=False)
        return df_corrections



def main():
    print("The code starts running here....")
    url = 'https://calendar.google.com/'
    path = 'data/input.html'

    fetch_and_save_data(url, path)  # web scrape

    model = CleanGPTModels()
    model.create_test_script(url,path)   # find violations


    model.input_df = model.add_severity_score(model.input_df, 'initialScore', 5)

    print("total # of violations: ", len(model.input_df))

    total_initial_severity_score = model.calculate_severity_score(model.input_df, 'initialScore')
    print("total initial severity score: ", total_initial_severity_score)

    model.create_corrected_dom_column(path)
    result_df = model.call_corrections2violations(url)

    total_final_severity_score = model.calculate_severity_score(result_df, 'finalScore')
    print("total final severity score: ", total_final_severity_score)

    total_improvement = ((1 - (total_final_severity_score / total_initial_severity_score)) * 100)
    print("total improvement: ", total_improvement, "%")

if __name__ == "__main__":
    main()