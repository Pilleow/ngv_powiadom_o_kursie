import re
import os


class HTMLGenerator:
    @staticmethod
    def generate_html(_html_template_dir: str, _verbose: bool = False, **kwargs) -> str:
        """
        Generate a HTML file based on a file template and a set of keyword arguments.
        :param html_template_dir: HTML template directory.
        :param kwargs: keyword=string pairs to swap in the HTML generator.
        :param verbose: If True, save a generated HTML file at the script location on completion.
        :return: HTML file contents as a string.
        """
        with open(_html_template_dir, 'r') as f:
            html_content = f.read()
        for k in kwargs:
            key = f"%%{k.upper()}%%"
            html_content = re.sub(key, kwargs[k], html_content)
        if _verbose:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            with open(f"{script_dir}/out_html.html", "w+") as f:
                f.write(html_content)
        return html_content

