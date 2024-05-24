function render() {
    const container = document.querySelector('#helloJavaScript');
    
    if (container) {
        let html = `<h3>This line was rendered with client-side JavaScript!!!</h3>`;
        html += `<p>
        Add JavaScript to your site by editing <code>src/theme/static/scripts/main.js</code>.
        </p>`;
        html += `<p>
        You can create as many modules as needed and import into <code>main.js</code>. 
        </p>`;
        container.innerHTML = html;
    }
}

render();