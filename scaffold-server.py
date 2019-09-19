import json 

'''
A script for scaffolding the RUSLAN Workshop server provided a list of names 
and a series of arguments determing which files to build. 
'''


# For every key X with a value Y in args, this function
# replaces all substrings in the template of the form '{X}' with 'Y'. 
def fill_template(template, args): 
  for key, value in args.items(): 
    template = template.replace(f'{{{key}}}', value)
  return template


def render_template(template_path=None, args=None): 
    with open(template_path) as t: 
        return fill_template(t.read(), args)


def load_group_names(file_path=''): 
    with open('group_names.txt' if file_path == '' else file_path) as fp: 
        return fp.readlines()


def usr_bool(user_answer): 
    return 'y' in user_answer.lower()


def build_docker_compose_services(api_names, database_names, volume_names, service_names, local=False, db_config=False): 
    services = []
    for api, db, volume, service in zip(api_names, database_names, volume_names, service_names): 
        service = f'''
        {render_template(
            template_path=
                'scaffold/misc/t-docker-compose-service-db' if db_config 
                else 'scaffold/misc/t-docker-compose-service-local' if local 
                else 'scaffold/misc/t-docker-compose-service',
            args={
                'database_name' : db, 
                'api_name' : api, 
                'volume' : volume,
                'service_path' : f'services/{service}'
            })}
        '''
        services.append(service)

    return '\n \n'.join(services)


def build_docker_compose_depends_on_list(api_names): 
    return '\n'.join([f'      - {api}' for api in api_names])


def build_docker_compose_volume_list(volumes): 
    return '\n'.join([f'  - {volume}:' for volume in volumes])


def build_docker_compose(api_names, database_names, volume_names, service_names, local=False, db_config=False): 
    services = build_docker_compose_services(api_names, database_names, volume_names, service_names, local=local, db_config=db_config)
    depends_on_list = build_docker_compose_depends_on_list(database_names if db_config else api_names)
    volume_list = build_docker_compose_volume_list(volume_names)

    build_path = 'docker-compose-db.yml' if db_config else 'docker-compose-db.yml' if local else 'docker-compose-db.yml'
    template_path = f'scaffolding/t-{build_path}'

    with open(build_path, 'w+') as fp: 
        fp.write(render_template(template_path=template_path, args={
            'services' : services,
            'depends_on_list' : depends_on_list, 
            'volume_list' : volume_list
        }))        

    
def build_dockerfiles(api_names, service_names, local=False): 
    for service_name, api_name in zip(service_names, api_names): 
        build_path = f'{service_name}/Dockerfile.local' if local else f'{service_name}/Dockerfile'
        template_path = 'scaffolding/services/Dockerfile.local' if local else 'scaffolding/services/Dockerfile'

        with open(build_path, 'w+') as fp: 
            fp.write(render_template(template_path=template_path, args={
                'api_name' : api_name
            }))



# Main entrypoint
if __name__ == "__main__": 
    group_names = load_group_names(input('Group name file path (default is "group_names.txt"): '))

    service_names =    [f'{group_name}Service' for group_name in group_names]
    api_names =        [f'{group_name}API' for group_name in group_names]
    docker_api_names = [f'{group_name.lower()}-api' for group_name in group_names]
    database_names =   [f'{group_name.lower()}-db' for group_name in group_names]
    volume_names =     [f'{group_name.lower()}-db-volume' for group_name in group_names]

    should_build_docker = usr_bool(input('''
        Should I build all Docker files for the projects (docker-compose.yml, docker-compose-local.yml, 
        docker-compose-db.yml, Dockerfile and Dockerfile.local for every project? [Y/n])'''))
    should_build_dotnet_projects = usr_bool(input(''' 
        Should I (re)build all .NET Web APIs, potentially overwriting existing projects? [Y/n]'''))
    should_build_nginx = usr_bool(input(''' 
        Should I build the nginx.conf and nginx.conf.local files redirecting to all projects?'''))

    if should_build_docker: 
        build_docker_compose(api_names, database_names, volume_names, service_names)
        build_docker_compose(api_names, database_names, volume_names, service_names, local=True)
        build_docker_compose(api_names, database_names, volume_names, service_names, db_config=True)
        build_dockerfiles(api_names, service_names)
        build_dockerfiles(api_names, service_names, local=True)


    if should_build_nginx: 
        pass 

    if should_build_dotnet_projects: 
        pass 


    

    
    print('Completed scaffolding.')