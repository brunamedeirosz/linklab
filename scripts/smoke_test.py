"""Verifica Django + proxy Vite com banco temporário, sem acessar sites externos."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    if not shutil.which('node'):
        raise SystemExit('Instale Node.js e execute npm ci em frontend primeiro.')
    results = ROOT / 'test-results'
    results.mkdir(exist_ok=True)
    processes = []
    with tempfile.TemporaryDirectory(dir=results) as directory:
        env = os.environ.copy()
        env.pop('POSTGRES_HOST', None)
        env['SQLITE_PATH'] = str(Path(directory) / 'smoke.sqlite3')
        env['DJANGO_DEBUG'] = 'true'
        env['DJANGO_ALLOWED_HOSTS'] = '127.0.0.1,localhost'
        env['SHORT_URL_BASE'] = 'http://127.0.0.1:18000'
        env['API_PROXY_TARGET'] = 'http://127.0.0.1:18000'
        env['VITE_API_BASE_URL'] = '/api'
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'],
                       cwd=ROOT / 'backend', env=env, check=True,
                       stdout=subprocess.DEVNULL, creationflags=flags)
        commands = [
            ([sys.executable, 'manage.py', 'runserver', '127.0.0.1:18000', '--noreload'], ROOT / 'backend'),
            (['node', 'node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '15173', '--strictPort'], ROOT / 'frontend'),
        ]
        try:
            for command, cwd in commands:
                processes.append(subprocess.Popen(command, cwd=cwd, env=env,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags))
            for url in ['http://127.0.0.1:18000/api/links/', 'http://127.0.0.1:15173/']:
                for _ in range(100):
                    if any(process.poll() is not None for process in processes):
                        raise RuntimeError('Servidor encerrou. Verifique se as portas 18000 e 15173 estão livres.')
                    try:
                        urllib.request.urlopen(url, timeout=1).close()
                        break
                    except urllib.error.HTTPError:
                        break  # 405 confirma que Django respondeu.
                    except urllib.error.URLError:
                        time.sleep(.1)
                else:
                    raise RuntimeError(f'Servidor não respondeu: {url}')
            base = 'http://127.0.0.1:15173'
            with urllib.request.urlopen(base, timeout=5) as response:
                assert 'LinkLab' in response.read().decode()
            request = urllib.request.Request(base + '/api/links/',
                data=json.dumps({'original_url': 'https://example.com/path?q=1'}).encode(),
                headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=5) as response:
                assert response.status == 201
                link = json.load(response)
            assert link['short_url'].startswith('http://127.0.0.1:18000/')
            try:
                urllib.request.build_opener(NoRedirect).open(link['short_url'], timeout=5)
            except urllib.error.HTTPError as response:
                assert response.code == 302
                assert response.headers['Location'] == 'https://example.com/path?q=1'
            else:
                raise AssertionError('Esperado redirecionamento 302')
            with urllib.request.urlopen(base + f"/api/links/{link['short_code']}/stats/", timeout=5) as response:
                stats = json.load(response)
                assert stats['click_count'] == 1
                assert stats['short_url'] == link['short_url']
            print('OK: página Vite, criação via proxy, redirecionamento 302 e estatísticas com 1 acesso.')
        finally:
            for process in processes:
                process.terminate()
            for process in processes:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == '__main__':
    main()
