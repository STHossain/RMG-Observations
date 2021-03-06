# -*- coding: utf-8 -*-
import console, datetime, json, os, pprint, sys, time, Image, photos

from RMG_utils import (get_timestamp, get_user_choice, get_user_input,
                       get_user_special_float, save_user_photo, get_user_photo)

'''
    Development: I have taken on board the comments of CCC in trying to rework the application.
        There were a few coding aspects that I did not understand. I have left comments to that
        effect which are recognisable by a #!! prefix.
'''

# ccc: I am not sure why we need get_user_choice_num() so I did not move it to RMG_utils.py
# RC: The user_choice_num() function is used in determining the task, the second element of the tuple that forms the
# taks dict keys is a code. The first number in that two digit code represents the task, the second the department.
# This is probably not the best way to do it, but was just one solution that I thought of. I think you suggested
# a named tuple, but I was not sure how to incorporate that at that time. 
def get_user_choice_num(in_title, in_prompt_and_choices, cancel = True):
    """ Returns number of user choice. If cancel = True then the user may cancel the dialogue, otherwise
        cancellations will be met with an hud error message """
    if cancel:
        user_choice = console.alert(in_title, *in_prompt_and_choices)
        return user_choice
    try:
        user_choice = console.alert(in_title, *in_prompt_and_choices)
        return user_choice
    except KeyboardInterrupt:
        pass
    Error = 'You may not cancel at this time'
    console.hud_alert(Error, 'error')
    return get_user_choice_num(in_title, in_prompt_and_choices, cancel = False)

def write_to_json(in_dict, file_name):
    ''' Function to save in_dict to json '''
    with open(file_name, 'w') as out_file:
        json.dump(in_dict, out_file)
    return

def open_json(file_name, function, f_args):
    ''' Function to open JSON. Returns json file if in directory else the function and arguments that will create
        the json'''
    #!! The idea here is to look for the json file that is passed as the file_name argument and if it is
    # not found in the working directory then the function that creates that file is invoked. For example,
    # upon first using the application the Top Level Output is not yet in existence. When this is the case
    # the routine for creating that will be invoked. 
    try:
        out_dict = json.load(open(file_name))
        return out_dict
    except IOError:
        return function(*f_args)

'''
The following task dictionary contains the names of the tasks that are envisaged (currently 3, although only one (wip)
is fully thought through at this stage). The tuple contains the json name in which data related to that task are/will
be stored, and a list of the variables that will be collected for each task.
'''

task_dict = {('Knitting_wip',      '11') : ('Knitting_wip.json',      ['Attendance', 'Style', 'WIP']),
             ('Linking_wip',       '12') : ('Linking_wip.json',       ['Attendance', 'Style', 'WIP']),
             ('Knitting_interact', '21') : ('Knitting_interact.json', ['enter_once_determined']),
             ('Linking_interact',  '22') : ('Linking_interact.json',  ['enter_once_determined']),
             ('Knitting_other',    '31') : ('Knitting_other.json',    ['enter_once_determined']),
             ('Linking_other',     '32') : ('Linking_other.json',     ['enter_once_determined'])}

def create_task_dicts(top_level_dict, task_dict):
    """ Function to create task dictionaries. This is designed to be called inside the configure application
        function. Saves each dict to .json """
    #!! This function seems a little erratic as it is based upon using sub-strings to determine how to
    # create the dictionaries. It seems to work, but I am concerned that a small change in the strings
    # entered either in the top_level_dict or the task_dict could prove fatal. At present this was the best
    # I could come up with. Return at a later date perhaps.

    for task in task_dict.keys():
        department = task[0].split('_')[0]
        task_dict_json = {'date_time' : []}
        task_dict_json.update({department[:2].upper() + str(serial_no) :
                                  {variable : [] for variable in task_dict[task][1]}
                                       for serial_no in xrange(1, top_level_dict[department] + 1)})
        write_to_json(task_dict_json, task_dict[task][0])

# RC: Should this be a global variable or could it be defined in the function? If global then why not pass it as an
# argument to the relevant function?
Top_validation_fmt = '''
You have entered the following data:

        'Knitting':         {Knitting}
        'Linking' :         {Linking}

Are you satisfied with this? '''

def configure_application(file_name):
    """ Creates and returns the top level dictionary and the task dictionaries. Additioanlly tests user satisfaction
        with the top level data entered and saves to json. It is intended that this is the function that is returned
        by the open_json function if the json does not already exist when opening the top_level_data."""
    #¡¡ I am not sure if this is really the right way to program these type of functions that return other
    # functions. This seems to work, but doubtless there is some coding style best practice I have overlooked.
    print 'First you need to conifgure the application for the number of operators to be observed'
    time.sleep(4)

    # create top level dictionary
    top_level_dict = { 'Knitting' : get_user_int('Please enter the number of Knitting Operators'),
                       'Linking'  : get_user_int('Please enter the number of Linking Operators') }

    print(Top_validation_fmt.format(**top_level_dict))  # print data back to user

    # check user satisfaction
    user_satisfied = get_user_choice('Are you satisfied with data entered?',
                                              'Select one', ('Yes', 'No'))
    if user_satisfied == 'No':
        return configure_application(file_name)

    # save to json
    write_to_json(top_level_dict, file_name)

    # Create and save the task dictionaries
    create_task_dicts(top_level_dict, task_dict)

    return top_level_dict

def create_id_dicts(top_level_dict, department):
    """ Creates and returns the a worker ID dict. The entry for each machine code is a dict containing two
            keys, the first will map to a string equal either to 'Manned' or 'Unmanned, and the second will map to a
            string equal to the worker id number or null."""
    # This function will create empty id_dicts, I have not yet been able to test it.
    dept_choice = department

    id_dict =         {'date_time' : str()}
    '''' ccc: the following code is broken!!
    id_dict.update( {dept_choice[:2].upper() + serial_no :
                                    {'mc_status' : str(), 'worker_id' : str()}
                                    for serial_no in xrange(1, top_level_dict[dept_choice] + 1)})
    '''
    return id_dict

def locate_most_recent(file_prefix):
    """ Function returns the most recent file that contains file_prefix if any exist"""
    # This function will search for the most recent daily id dict. If there are none it returns None.
    # I have not had a chance to test it.
    file_list = os.listdir(os.getcwd())
    prefix_file_list = [file for file in file_list if file_prefix in file]
    if not prefix_file_list:
        return None #Not sure about this yet, return to it.
    date_list = [date for date in [file.split('-')[1] for file in prefix_file_list]]
    # Note the character on which to split the file name is currently '-'
    datetime_list = [datetime.datetime.strptime(date, '%Y_%m_%d_%H_%M') for date in date_list]
    most_recent_date = max(datetime_list)
    most_recent_file = file_prefix + '-' + most_recent_date.strftime('%Y_%m_%d_%H_%M')
    return most_recent_file

ID_validation_fmt = '''
You have entered the following data:

        'Machine Status'        :         {mc_status}
        'Worker ID'                 :         {worker_id}

Are you satisfied with this? '''

ID_validation_fmt_2 = '''
The most recent available data for this machine are:

        'Machine Status'        :         {mc_status}
        'Worker ID'                 :         {worker_id}

Are you satisfied with this? '''


def worker_id(machine_code):
    """ Function prompts user for informaiton about the machine and the id of the operator working the machine 
	(if any). Returns dict of that information"""
    # This generates the worker routine for an individual operator. Rather than thinking about
    # present/absent the user will simply state is the machine is manned or unmanned. If it is
    # manned they will be prompted to enter the worker id of the person working on the machine.
    # The fact that manned/unmanned status will be dealt with here means that the Attendance
    #component of the wip task is now defunct (although the user may wish to change the
    # manned/unmanned status during the task if for example the worker was absent when the id
    # routine is run, but present once the wip task is undertaken.
    console.clear()
    print('For machine {} please enter thee following information: \n'.format(machine_code))

    worker_id_dict = { 'mc_status' : 'Unmanned',
                                           'worker_id' : 'null'}

    title = '{} : Please state is machine is manned or unmanned?'.format(machine_code)
    user_choice = get_user_choice(title, 'Please select an option',
                                              ('Manned', 'Unmanned'))

    # If machine unmanned
    if user_choice != 'Manned':
        print ID_validation_fmt.format(machine_code, **worker_id_dict)  # print data back to user
        time.sleep(2)

        #check user satisfaction
        user_satisfied = get_user_choice('Are you satisfied with data entered?',
                                                      'Select one', ('Yes', 'No'))
        if user_satisfied == 'No':
            return worker_id(machine_code)  # re-enter the machine dict data

        return worker_id_dict  # return the machine dict

    worker_id_dict['mc_status'] = 'Manned'
    prompt = 'Please enter the id number of the worker on this machine as is appears on their ID card: '
    worker_id_dict['worker_id'] = get_user_input(prompt).strip().lower()
    print ID_validation_fmt.format(machine_code, **worker_id_dict) # print data back to user
    time.sleep(4)

    user_satisfied = get_user_choice('Are you satisfied with data entered?',
                                               'Select one', ('Yes', 'No'))
    if user_satisfied == 'No':
        return worker_id(machine_code) #re-enter worker wip data

    return worker_id_dict #return the worker id dict

def create_machine_code(top_level_dict, department):
    """ Function returns a list of the worker codes. """
    #!! This is somewhat surplus to requirements. The issue is that running though the worker codes in the
    # dictionary json presents the codes out of order. Perhaps an ordered dict could be used instead?

    return [department[:2].upper() + str(serial_no) for serial_no
                      in xrange(1, top_level_dict[department] + 1)]

def populate_first_id_dict(id_dict, top_level_dict, department):
    """ Function to populate the worker id dicts for the first time """
    # If no daily_id dicts exist then this function will create the first instance of that dict by
    # prompting user for the relevant informaiton by calling the worker_id function. I have not yet
    # had the chance to see if this works.
    # ccc: this code is broken: id_dict['date_time'].append(get_timestamp())
    for machine_code in create_machine_code(top_level_dict, department):
        worker_id_dict = worker_id(machine_code)
        id_dict[machine_code]['mc_status'] = worker_id_dict['mc_status']
        id_dict[machine_code]['worker_id'] = worker_id_dict['worker_id']
    return id_dict

def populate_id_dict(id_dict, past_id_dict_file_name, top_level_dict, department):
    """ Function to populate worker id dicts based upon previous saved versions """
    # This function populates the daily id dict but rather than asking the user for each piece of
    # information it takes the last known data for that machine and prompts the user to see if
    # they wish to make changes. If they do the the worker_id function is called. I have not yet
    # had the chance to see if this is working.
    if past_id_dict_file_name is None:
        return populate_first_id_dict(id_dict, top_level_dict, department)

    past_id_dict = open_json(past_id_dict_file_name, None, None)
    for machine_code in create_machine_code(top_level_dict, department):
        print ID_validation_fmt.format_2(machine_code, **past_id_dict[machine_code]) # print data back to user
        user_satisfied = get_user_choice('Are you satisfied with data entered?',
                                                 'Select one', ('Yes', 'No'))
        if user_satisfied == 'Yes':
            id_dict[machine_code]['mc_status'] = past_id_dict[machine_code]['mc_status']
            id_dict[machine_code]['worker_id'] = past_id_dict[machine_code]['worker_id']
        else:
            update_id_dict = worker_id(machine_code)
            id_dict[machine_code]['mc_status'] = update_id_dict['mc_status']
            id_dict[machine_code]['worker_id'] = update_id_dict['worker_id']
    return id_dict


def id_daily_routine(file_prefix, top_level_dict):
    """ Function that controls the id daily_routine"""
    # I worry that this is not very elegant, and I have not yet been able to test it. The idea
    # is that this function controls the entire routine of worker id. In particular I worry
    # about all of the functions calling other functions as part of this routine. It seems like
    # the complexity might make the program hard to debug.

    daily_file = locate_most_recent(file_prefix + '_id')
    if daily_file is None:
        return populate_id_dict(create_id_dicts(top_level_dict, file_prefix), daily_file, top_level_dict, file_prefix)
    if get_timestamp()[:10] not in daily_file:
        return populate_id_dict(create_id_dicts(top_level_dict, file_prefix), daily_file, top_level_dict, file_prefix)
    else:
        return open_json(daily_file, None, None)

def determine_task(user_task_dict = task_dict):
    ''' Function prompts user to determine which task is to be undertaken and return the key (a tuple) that relates
        to that task fom the task_dict'''

    task_choice = str(get_user_choice_num('Select a task',
                            'Please select a task to complete',
                            ('Work in progress', 'Interactions','Other')))
    #¡¡ This allows a cancel by the user, but it will crash the program, is that what I want? Not sure.

    dept_choice = str(get_user_choice_num('Select a department',
                            'Please select which department to work in',
                            ('Knitting', 'Linking')))

    user_task_choice = task_choice + dept_choice

    for task_tuple in task_dict.keys():
        if user_task_choice in task_tuple:
            return task_tuple

#A string that is used to display the wip data back to the user
wip_validation_fmt = ''' You have entered the following data for machine {}:

    'Attendance' : {Attendance}
    'Style'.     : {Style}
    'WIP'        : {WIP}

Are you satisfied with this?'''

def worker_wip(machine_code):
    ### This needs to be updated to reflect the fact that the worker_id task will now deal with the issue
    ### of machines being manned (operator present) or unmanned (operator absent or otherwise not there).
    """ Function to create individual machine WIP dict """

    console.clear()
    print('For machine {} please enter thee following information: \n'.format(machine_code))

    # Machine wip dictionary
    # The attendance no longer necessary once the ID number routine complete
    machine_dict = { 'Attendance' : 'Absent',
                     'Style'      : 'null',
                     'WIP'        : 'null' }
    # Determine absence
    user_choice = get_user_choice('{} : Is the operator present?'.format(machine_code),
                                            'Please select an option', ('Present', 'Absent',))
    # If operator not present
    if user_choice != 'Present':
        print wip_validation_fmt.format(machine_code, **machine_dict)  # print data back to user
        time.sleep(2)

        #check user satisfaction
        user_satisfied = get_user_choice('Are you satisfied with data entered?',
                                         'Select one', ('Yes', 'No'))
        if user_satisfied == 'No':
            return worker_wip(machine_code)  # re-enter worker wip data

        return machine_dict  # return the worker wip dict

    # If operator present
    machine_dict['Attendance'] ='Present'
    prompt = 'Please enter current style name/number as per work order: '
    machine_dict['Style'] = get_user_input(prompt).strip().lower()
    prompt = 'Please enter the amount of WIP at time of checking: '
    machine_dict['WIP'] = get_user_special_float(prompt)

    print wip_validation_fmt.format(machine_code, **machine_dict) # print data back to user
    time.sleep(4)

    user_satisfied = get_user_choice('Are you satisfied with data entered?',
                                               'Select one', ('Yes', 'No'))
    if user_satisfied == 'No':
        return worker_wip(machine_code) #re-enter worker wip data

    return machine_dict #return the worker wip dict

def wip_task(task_tuple, top_level_dict, task_data_dict):
    """ Updates relevant wip data dictionary """

    task_data_dict['date_time'].append(get_timestamp())
    department = task_tuple[0].split('_')[0]
    for machine_code in create_machine_code(top_level_dict, department):
        worker_wip_dict = worker_wip(machine_code)
        for data_point in task_data_dict[machine_code]:
            task_data_dict[machine_code][data_point].append(worker_wip_dict[data_point])

    return task_data_dict

def interact_task():
    # complete once defined
    print('TBC')
    return

def other_task():
    # complete once defined
    print 'TBC'
    return

def initiate_task(task_tuple, task_function_dict):
    task = task_tuple[0].split('_')[1]
    return task_function_dict[task][0](*task_function_dict[task][1])

def main(argv):
    console.clear()
    print 'Welcome to RMG Observations'
    top_level_dict = open_json('top_level_data.json', configure_application, ('top_level_data.json',))
    today_knitting_id_dict = id_daily_routine('Knitting', top_level_dict)
    today_linking_id_dict  = id_daily_routine('Linking', top_level_dict)
    task_tuple = determine_task()
    task_file_name = task_dict[task_tuple][0]
    task_data_dict = open_json(task_file_name, None, None)

    task_function_dict = {'wip'      : (wip_task, (task_tuple, top_level_dict, task_data_dict)),
                          'interact' : (interact_task, (())),
                           'other'   : (other_task, (())) }
    modified_task_dict = initiate_task(task_tuple, task_function_dict)
    write_to_json(modified_task_dict, task_file_name)
    save_user_photo(get_user_photo(), task_tuple[0])

    ''' see: http://docs.python.org/2/tutorial/modules.html#executing-modules-as-scripts '''

if __name__ == '__main__':
    sys.exit(main(sys.argv))
