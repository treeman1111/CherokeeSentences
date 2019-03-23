

window.onload = () => {
    let cherokee_input = document.querySelector('input#chr_search');
    let english_input = document.querySelector('input#en_search');
    let search_button = document.querySelector('div#search');
    let container = document.querySelector('div#container');

    search_button.addEventListener('click', () => {
        // clear the contents of the container prior to loading new ones
        let first_child = container.firstChild;

        while (first_child) {
            container.removeChild(first_child);
            first_child = container.firstChild;
        }
        // now we've finished dumping the old child nodes and can add new ones

        // send a request for the ids of the sentences which match the search
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (this.status == 200 && this.readyState == 4) {
                results = JSON.parse(this.responseText);

                // iterate over each of the ids and populate the container with the resultant info
                results['ids'].forEach(result => {
                    let request = new XMLHttpRequest();
                    request.onreadystatechange = function () {
                        if (this.status == 200 && this.readyState == 4) {
                            sentence = JSON.parse(this.responseText);

                            let cherokee_div = document.createElement('div');
                            let cherokee_text = document.createTextNode(`${sentence['cherokee']}`);
                            let english_div = document.createElement('div');
                            let english_text = document.createTextNode(`${sentence['english']}`);
                            let work_div = document.createElement('div');
                            let work_text = document.createTextNode(`${sentence['work']}`);
                            let wrapper_div = document.createElement('div');

                            cherokee_div.appendChild(cherokee_text);
                            english_div.appendChild(english_text);
                            work_div.appendChild(work_text);

                            cherokee_div.className = 'cherokee'
                            english_div.className = 'english'
                            work_div.className = 'work'
                            wrapper_div.className = 'wrapper'

                            wrapper_div.appendChild(cherokee_div);
                            wrapper_div.appendChild(english_div);
                            wrapper_div.appendChild(work_div);

                            container.appendChild(wrapper_div);
                        }
                    }
                    request.open('GET', `/sentences?id=${result}`, true);
                    request.send();
                });
            }
        };
        xhr.open('GET', `/sentences?type=json&chr_frag=${cherokee_input.value}&en_frag=${english_input.value}`, true);
        xhr.send();
    });
}