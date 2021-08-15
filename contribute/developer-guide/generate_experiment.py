from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml
import os
import sys
import argparse
import glob
import shutil

# generate_csv creates __init__.py file which helps python to find the corresponding module
def generate_init(init_path):
    init_path = init_path  + '/' + '__init__.py'
    open(init_path, mode='a').close()

# generate_csv creates the experiment chartserviceversion manifest
def generate_csv(csv_parent_path, csv_name, csv_config, litmus_env):
    
    csv_filename = csv_parent_path + '/' + csv_name + '.' + 'experiment_chartserviceversion.yaml'
    # Load Jinja2 template
    template = litmus_env.get_template('./templates/experiment_chartserviceversion.tmpl')
    output_from_parsed_template = template.render(csv_config)
    with open(csv_filename, "w") as f:
        f.write(output_from_parsed_template)

# generate_csv creates the category chartserviceversion manifest
def generate_csv_cat(csv_parent_path, csv_name, csv_config, litmus_env):
    
    csv_filename = csv_parent_path + '/' + csv_name + '.' + 'category_chartserviceversion.yaml'
    
    # Load Jinja2 template
    template = litmus_env.get_template('./templates/category_chartserviceversion.tmpl')
    output_from_parsed_template = template.render(csv_config)
    with open(csv_filename, "w") as f:
        f.write(output_from_parsed_template)

# generate_chart creates the experiment custom resource manifest
def generate_chart(chart_parent_path, chart_config, litmus_env):
    chart_filename = chart_parent_path + '/' + 'experiment.yaml'

    # Load Jinja2 template
    template = litmus_env.get_template('./templates/experiment_custom_resource.tmpl')
    output_from_parsed_template = template.render(chart_config)
    with open(chart_filename, "w") as f:
        f.write(output_from_parsed_template)

# generate_rbac creates the rbac for the experiment
def generate_rbac(chart_parent_path, chart_config, litmus_env):
    rbac_filename = chart_parent_path + '/' + 'rbac.yaml'

    # Load Jinja2 template
    template = litmus_env.get_template('./templates/experiment_rbac.tmpl')
    output_from_parsed_template = template.render(chart_config)
    with open(rbac_filename, "w") as f:
        f.write(output_from_parsed_template)

# generate_engine creates the chaos engine for the experiment
def generate_engine(chart_parent_path, chart_config, litmus_env):
    engine_filename = chart_parent_path + '/' + 'engine.yaml'

    # Load Jinja2 template
    template = litmus_env.get_template('./templates/experiment_engine.tmpl')
    output_from_parsed_template = template.render(chart_config)
    with open(engine_filename, "w") as f:
        f.write(output_from_parsed_template)

# generate_chaoslib creates the chaosLib for the experiment
def generate_chaoslib(chaoslib_parent_path, chaoslib_name, chaoslib_config, litmus_env):
    chaoslib_filename = chaoslib_parent_path + '/' + chaoslib_name + '.py'

    create_dir(chaoslib_parent_path)
        
    # Load Jinja2 template
    template = litmus_env.get_template('./templates/chaoslib.tmpl')
    output_from_parsed_template = template.render(chaoslib_config)
    with open(chaoslib_filename, "w") as f:
        f.write(output_from_parsed_template)
    
    # generate __init__.py file
    generate_init(chaoslib_parent_path)

# generate_environment creates the environment for the experiment
def generate_environment(environment_parent_path, environment_config, litmus_env):
    environment_filename = environment_parent_path + '/environment.py'

    create_dir(environment_parent_path)

    # Load Jinja2 template
    template = litmus_env.get_template('./templates/environment.tmpl')
    output_from_parsed_template = template.render(environment_config)
    with open(environment_filename, "w") as f:
        f.write(output_from_parsed_template)

    # generate __init__.py file
    generate_init(environment_parent_path)

# generate_types creates the types.py for the experiment
def generate_types(types_parent_path, types_config, litmus_env):
    types_filename = types_parent_path + '/types.py'

    create_dir(types_parent_path)
  
    # Load Jinja2 template
    template = litmus_env.get_template('./templates/types.tmpl')
    output_from_parsed_template = template.render(types_config)
    with open(types_filename, "w") as f:
        f.write(output_from_parsed_template)

    # generate __init__.py file   
    generate_init(types_parent_path)

# generate_k8s_deployment creates the experiment kubernetes deployment manifest
def generate_k8s_deployment(k8s_parent_path, k8s_config, litmus_env):
    k8s_filename = k8s_parent_path + '/' + 'test.yml'

    # Load Jinja2 template
    template = litmus_env.get_template('./templates/experiment_k8s_deployment.tmpl')
    output_from_parsed_template = template.render(k8s_config)
    with open(k8s_filename, "w") as f:
        f.write(output_from_parsed_template)

# generate_experiment creates the expriment.py file
def generate_experiment(experiment_parent_path, experiment_name, experiment_config, litmus_env):
    experiment_filename = experiment_parent_path + '/' + experiment_name + '.py'
    
    # Load Jinja2 template
    template = litmus_env.get_template('./templates/experiment.tmpl')
    output_from_parsed_template = template.render(experiment_config)
    with open(experiment_filename, "w+") as f:
        f.write(output_from_parsed_template)

    # generate __init__.py file
    generate_init(experiment_parent_path)

# generate_package creates the package manifest
def generate_package(package_parent_path, config, package_name, litmus_env):
    package_filename = package_parent_path + '/' + package_name + '.package.yaml'
    
    # Load Jinja2 template
    template = litmus_env.get_template('./templates/package.tmpl')
    output_package = template.render(config)
    with open(package_filename, "w") as f:
        f.write(output_package)

# create_dir create new directory
def create_dir(path):
    if os.path.isdir(path) != True:
        os.makedirs(path)

def generate_icon(chart_parent_path, litmus_root, image_name, litmus_env):
    src_dir = litmus_root + "/contribute/developer-guide/icons/"
    dst_dir = chart_parent_path + '/' + "icons/"
    create_dir(dst_dir)
    
    for jpgfile in glob.iglob(os.path.join(src_dir, "k8s.png")):
        shutil.copy(jpgfile, dst_dir)
        os.rename(dst_dir + '/' + 'k8s.png', dst_dir + '/' + image_name +'.png')
        
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, default="attributes.yaml",
                        help="metadata to generate experiment_chartserviceversion yaml")
    parser.add_argument("-g", "--generate", required=True, default="experiment",
                        help="scaffold a new chart or experiment into existing chart")
    parser.add_argument("-t", "--type", required=False, default="all",
                        help="type of the chaos chart")
    args = parser.parse_args()

    entity_metadata_source = args.file
    entity_type = args.generate
    chartType = args.type
    
    # Load data from YAML file into a dictionary
    # scalar values to Python the dictionary format
    # YAML document to a Python object.
    with open(entity_metadata_source) as f:
        config = yaml.safe_load(f)
    
    # get name and category
    entity_name = config['name']
    category_name = config['category']
    
    env = Environment(loader = FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True, autoescape=select_autoescape(['yaml']))
    
    # store the litmus root from bootstrap folder
    litmus_root = os.path.abspath(os.path.join("..", os.pardir))
    
    # initilise directories
    exp_root_dir = litmus_root + '/experiments/' + '/' + config['category']
    create_dir(exp_root_dir)
    experiment_root_dir = exp_root_dir + '/' + config['name']
    create_dir(experiment_root_dir)
    generate_init(exp_root_dir)

    # if generate_type is chart, only generate the chart(top)-level CSV & package manifests 
    if entity_type == 'chart':
        
        # initilise chart directory
        chart_dir = experiment_root_dir + '/charts'
        create_dir(chart_dir)

        if chartType == "category" or chartType == "all":
			
            # generate icon for category
            generate_icon(chart_dir, litmus_root, category_name, env)
            
            # generate category chartserviceversion
            generate_csv_cat(chart_dir, category_name, config, env) 
            
            # generate package
            generate_package(chart_dir, config, category_name, env)
        
        if chartType == "experiment" or chartType == "all":
			
            # generate icon for category
            generate_icon(chart_dir, litmus_root, entity_name, env)

            # generate experiment charts
            generate_csv(chart_dir, entity_name, config, env)

            # generate experiment-custom-resource
            generate_chart(chart_dir, config, env)

            # generate experiment specific rbac
            generate_rbac(chart_dir, config, env)

            # generate experiment specific chaos engine
            generate_engine(chart_dir, config, env)
        
        if chartType != "experiment" and chartType != "category" and chartType != "all":
            print("Provided --chartType={} flag is invalid".format(chartType))
            return
        print("chart created successfully")
    # if generate_type is experiment, generate the litmusbook arefacts
    elif entity_type == 'experiment':
        
        # initilise experiment directory
        experiment_dir = experiment_root_dir + '/experiment'
        create_dir(experiment_dir)
        
        # initialise test directory
        test_dir = experiment_root_dir + '/test'
        create_dir(test_dir)

        # generate __init__.py file in root experiment dir
        generate_init(experiment_root_dir)
        
        # initialise chaosLib, environment and types directory
        chaoslib_dir = litmus_root + '/chaosLib/litmus/' + config['name'] + '/lib'
        environment_dir = litmus_root + '/pkg/' + config['category'] + '/environment'
        types_dir = litmus_root + '/pkg/' + config['category'] + '/types'
        
        # create and generate __init__.py file in chaosLib experiment dir 
        create_dir(litmus_root + '/chaosLib/litmus/' + config['name'])
        generate_init(litmus_root + '/chaosLib/litmus/' + config['name'])
        
        # generate experiment.py
        generate_experiment(experiment_dir, entity_name, config, env)

        # generate chaosLib
        generate_chaoslib(chaoslib_dir, entity_name, config, env)

        # generate environment.py 
        generate_environment(environment_dir, config, env)

        # generate environment.py 
        generate_types(types_dir, config, env)

        # generate k8s deployment
        generate_k8s_deployment(test_dir, config, env)

        generate_init(litmus_root + '/pkg/' + config['category'])

        print("experiment created successfully")
    else:
        print("Provided --generate={} flag is invalid".format(entity_type))

if __name__=="__main__":
    main()
