import os
from flask import Flask, request, render_template
import psycopg2

application = Flask(__name__)

conn = psycopg2.connect(dbname="atc", user="*", password="*", host="*")
cur = conn.cursor()

port = int(os.getenv("PORT"))

CONCOURSE_URL = 'https://pcf-rabbitmq.ci.cf-app.com/teams/main/'
DEFAULT_PIPELINE = 'rabbitmq-1.13'
DEFAULT_CONCOURSE_URL = CONCOURSE_URL + '/pipelines/' + DEFAULT_PIPELINE

@application.route('/', methods=['GET'])
def blackbox():
    concourse = DEFAULT_CONCOURSE_URL
    return render_template('home.html', concourse_url=concourse)


@application.route('/', methods=['POST'])
def blackbox_submit():
    search_term = request.form['search-query']
    pipelines = 'rabbitmq-1.1[23]'
    if search_term.find('pipeline:') != -1:
        index = search_term.find('pipeline:')
        pipelines = search_term[index + len('pipeline:'):]
        search_term = search_term[:index]
    concourse = DEFAULT_CONCOURSE_URL

    print("QUERY:", search_term)
    try:
        cur.execute("""
                    select pipelines.name, jobs.name, builds.name, builds.id, build_events.event_id, build_events.payload
                    from build_events, builds, jobs, pipelines where
                    build_events.build_id=builds.id
                    and pipelines.name ~ %s
                    and builds.job_id = jobs.id
                    and builds.pipeline_id = pipelines.id
                    and status='failed'
                    and payload like '%%' || %s || '%%'
                    order by builds.start_time desc
                    limit 30
                    """, (pipelines, search_term))
        failures_rows = cur.fetchall()
        failures = []
        for failure_row in failures_rows:
            failure = {
                'pipeline': failure_row[0],
                'job': failure_row[1],
                'build_name': failure_row[2],
                'build_id': failure_row[3],
                'event_id': failure_row[4],
                'payload': failure_row[5]
            }
            failure['link'] = CONCOURSE_URL + '/pipelines/' + failure['pipeline'] + '/jobs/' + failure['job'] + '/builds/' + failure['build_name']
            failures.append(failure)

        cur.execute("""
                    select count(*)
                    from build_events, builds, jobs, pipelines where
                    build_events.build_id=builds.id
                    and pipelines.name ~ %s
                    and builds.job_id = jobs.id
                    and builds.pipeline_id = pipelines.id
                    and status='failed'
                    and payload like '%%' || %s || '%%'
                    """, (pipelines, search_term))
        count_row = cur.fetchall()
        count = count_row[0][0]

        return render_template('home.html', failures=failures, concourse_url=concourse, count=count, query=search_term)
    except Exception as e:
        print("Error when searching for query", e)
        return render_template('home.html', error=e, concourse_url=concourse)



if __name__ == '__main__':
    application.debug = True
    application.run(host='0.0.0.0', port=port)
