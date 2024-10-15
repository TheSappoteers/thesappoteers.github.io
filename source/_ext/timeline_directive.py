import json
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.docutils import SphinxDirective

class TimelineDirective(SphinxDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        # Load email data from a JSON file
        data_file = Path(self.env.srcdir) / 'email_data.json'
        with data_file.open(encoding='utf-8') as f:
            email_data = json.load(f)

        # Convert email data to timeline format
        timeline_data = [
            {
                "id": idx,
                "content": f"<strong>{email['subject']}</strong><br>{email['date']}",
                "start": email['date'],
                "group": email['sender'],
                "year": email['date'][:4],
                "subject": email['subject'],
                "sender": email['sender'],
                "flyer_image": email['flyer_image'],
                "body": email.get('body', 'No content available')
            }
            for idx, email in enumerate(email_data)
        ]

        # Create a div to hold the timeline and email detail
        timeline_div = nodes.raw('', '''
            <div id="timeline-container">
                <div id="timeline-filters"></div>
                <div id="timeline"></div>
                <div id="email-detail" style="display:none; margin-top: 20px; padding: 10px; border: 1px solid #ddd;">
                    <div class="email-header">
                        <h3 id="email-subject" class="email-subject"></h3>
                        <p id="email-sender" class="email-sender"></p>
                        <p id="email-date" class="email-date"></p>
                    </div>
                    <div id="email-body" class="email-body"></div>
                    <img id="email-flyer" style="max-width:100%; margin-top:10px;">
                </div>
            </div>
        ''', format='html')

        # Create a script to initialize the timeline
        script = nodes.raw('', f"""
        <script type="text/javascript">
            var container = document.getElementById('timeline');
            var items = new vis.DataSet({json.dumps(timeline_data, ensure_ascii=False)});
            var options = {{
                showCurrentTime: false,
                height: '400px',
                className: 'pydata-timeline',
                item: {{
                    className: 'pydata-timeline-item'
                }}
            }};
            var timeline = new vis.Timeline(container, items, options);

            // Create year filter
            var yearFilter = document.createElement('select');
            yearFilter.id = 'year-filter';
            var years = Array.from(new Set(items.get().map(item => item.year))).sort();
            yearFilter.innerHTML = '<option value="all">All Years</option>' +
                years.map(year => `<option value="${{year}}">${{year}}</option>`).join('');
            document.getElementById('timeline-filters').appendChild(yearFilter);

            // Create sender filter with unique names
            var senderFilter = document.createElement('select');
            senderFilter.id = 'sender-filter';
            var senders = Array.from(new Set(items.get().map(item => item.group.split('<')[0].trim()))).sort();
            senderFilter.innerHTML = '<option value="all">All Senders</option>' +
                senders.map(sender => `<option value="${{sender}}">${{sender}}</option>`).join('');
            document.getElementById('timeline-filters').appendChild(senderFilter);

            // Filter function
            function applyFilters() {{
                var selectedYear = yearFilter.value;
                var selectedSender = senderFilter.value;
                var filteredItems = items.get().filter(item => 
                    (selectedYear === 'all' || item.year === selectedYear) &&
                    (selectedSender === 'all' || item.group.startsWith(selectedSender))
                );
                timeline.setItems(new vis.DataSet(filteredItems));
            }}

            // Add event listeners to filters
            yearFilter.addEventListener('change', applyFilters);
            senderFilter.addEventListener('change', applyFilters);

            // Function to display email details
            function showEmailDetail(properties) {{
                var emailDetail = document.getElementById('email-detail');
                document.getElementById('email-subject').textContent = properties.subject;
                document.getElementById('email-sender').textContent = 'From: ' + properties.sender;
                document.getElementById('email-date').textContent = 'Date: ' + properties.start;
                
                // Display the HTML content of the email
                document.getElementById('email-body').innerHTML = properties.body;
                
                var flyerImg = document.getElementById('email-flyer');
                if (properties.flyer_image) {{
                    flyerImg.src = properties.flyer_image;
                    flyerImg.style.display = 'block';
                }} else {{
                    flyerImg.style.display = 'none';
                }}
                emailDetail.style.display = 'block';
            }}

            // Add click event to timeline items
            timeline.on('select', function(properties) {{
                if (properties.items.length) {{
                    var selectedId = properties.items[0];
                    var selectedItem = items.get(selectedId);
                    showEmailDetail(selectedItem);
                }}
            }});
        </script>
        """, format='html')

        return [timeline_div, script]

def setup(app):
    app.add_directive("timeline", TimelineDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }