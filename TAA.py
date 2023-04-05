from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['action'] == 'create_project':
            # code to create new project
            return 'New project created!'
        elif request.form['action'] == 'load_project':
            # code to load previous project
            return 'Project loaded!'
        elif request.form['action'] == 'analyze_task':
            selected_task = request.form['selected_task']
            # code to analyze selected task
            return f'Task {selected_task} analyzed!'
    else:
        selected_task = request.args.get('selected_task', 'novel')
        boxes_html = get_parameter_boxes(selected_task)
        return render_template('index.html', boxes_html=boxes_html)


@app.route('/get_parameters', methods=['GET'])
def get_parameters():
    selected_task = request.args.get('selected_task', 'novel')
    boxes_html = get_parameter_boxes(selected_task)
    return boxes_html


def get_parameter_boxes(selected_task):
    # Read the JSON file for the selected task
    json_file = f'Bin/hyp_{selected_task}.json'
    with open(json_file) as f:
        data = json.load(f)

    # Generate the HTML code for the parameter boxes
    boxes = []
    for key in data:
        box = f'<div class="box"><label for="{key}">{key}:</label><input type="text" name="{key}" value="{data[key]}"></div>'
        boxes.append(box)

    # Join the HTML code for each box into a single string
    boxes_html = '\n'.join(boxes)

    # Return the HTML code for the parameter boxes
    return boxes_html


@app.route('/create_project', methods=['POST'])
def create_project():
    project_name = request.form['project_name']
    # code to create new project using project_name
    return 'New project created with name: ' + project_name


if __name__ == '__main__':
    app.run(debug=True)