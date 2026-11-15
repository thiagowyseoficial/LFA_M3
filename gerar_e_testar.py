"""Gera máquinas de Turing determinísticas de uma fita no formato JFLAP."""
from pathlib import Path
import itertools
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


class MT:
    def __init__(self, nome):
        self.nome = nome
        self.states = []
        self.transitions = {}
        self.finals = set()

    def state(self, name):
        if name not in self.states:
            self.states.append(name)

    def add(self, src, chars, dst, write=None, move='R'):
        self.state(src)
        self.state(dst)
        for char in chars:
            assert (src, char) not in self.transitions, (src, char)
            self.transitions[src, char] = (dst, char if write is None else write, move)

    def final(self, name='aceita'):
        self.state(name)
        self.finals.add(name)

    def save(self):
        root = ET.Element('structure')
        ET.SubElement(root, 'type').text = 'turing'
        ET.SubElement(root, 'tapes').text = '1'
        automaton = ET.SubElement(root, 'automaton')
        ids = {s: str(i) for i, s in enumerate(self.states)}
        for i, s in enumerate(self.states):
            node = ET.SubElement(automaton, 'state', id=ids[s], name=f'q{i}')
            ET.SubElement(node, 'x').text = str(100 + (i % 6) * 210)
            ET.SubElement(node, 'y').text = str(100 + (i // 6) * 160)
            if i == 0:
                ET.SubElement(node, 'initial')
            if s in self.finals:
                ET.SubElement(node, 'final')
        for (src, read), (dst, write, move) in self.transitions.items():
            node = ET.SubElement(automaton, 'transition')
            ET.SubElement(node, 'from').text = ids[src]
            ET.SubElement(node, 'to').text = ids[dst]
            ET.SubElement(node, 'read', tape='1').text = read or None
            ET.SubElement(node, 'write', tape='1').text = write or None
            ET.SubElement(node, 'move', tape='1').text = move
        ET.indent(root)
        ET.ElementTree(root).write(ROOT / self.nome, encoding='utf-8', xml_declaration=True)

    def run(self, entrada, limit=2_000_000):
        tape = dict(enumerate(entrada))
        head, state = 0, self.states[0]
        for steps in range(limit):
            if state in self.finals:
                cells = [i for i, v in tape.items() if v]
                result = ''.join(tape.get(i, '') or ' ' for i in range(min(cells), max(cells)+1)) if cells else ''
                return True, result, steps
            transition = self.transitions.get((state, tape.get(head, '')))
            if transition is None:
                return False, '', steps
            state, tape[head], move = transition
            head += {'R': 1, 'L': -1, 'S': 0}[move]
        raise AssertionError(f'Limite de passos: {self.nome}: {entrada}')


def validate_pair(m):
    m.add('inicio', '01', 'valida_esquerda')
    m.add('valida_esquerda', '01', 'valida_esquerda')
    m.add('valida_esquerda', '+#', 'primeiro_direita', write='+')
    m.add('primeiro_direita', '01', 'valida_direita')
    m.add('valida_direita', '01', 'valida_direita')
    m.add('valida_direita', [''], 'retorna_inicio', move='L')
    m.add('retorna_inicio', '01+', 'retorna_inicio', move='L')
    m.add('retorna_inicio', [''], 'prepara', move='R')


def dobro():
    m = MT('01_multiplicar_por_dois.jff')
    m.add('inicio', '01', 'percorre')
    m.add('percorre', '01', 'percorre')
    m.add('percorre', [''], 'aceita', write='0', move='S')
    m.final()
    return m


def soma():
    m = MT('02_soma_binaria.jff')
    validate_pair(m)
    m.add('prepara', '01', 'prepara')
    m.add('prepara', '+', 'verifica_segundo')
    m.add('verifica_segundo', '0', 'verifica_segundo')
    m.add('verifica_segundo', '1', 'busca_fim')
    m.add('verifica_segundo', [''], 'limpa_segundo', move='L')
    m.add('busca_fim', '01', 'busca_fim')
    m.add('busca_fim', [''], 'decrementa', move='L')
    m.add('decrementa', '0', 'decrementa', write='1', move='L')
    m.add('decrementa', '1', 'volta_separador', write='0', move='L')
    m.add('volta_separador', '01', 'volta_separador', move='L')
    m.add('volta_separador', '+', 'incrementa', move='L')
    m.add('incrementa', '1', 'incrementa', write='0', move='L')
    m.add('incrementa', ['0', ''], 'prepara', write='1')
    m.add('limpa_segundo', '0', 'limpa_segundo', write='', move='L')
    m.add('limpa_segundo', '+', 'aceita', write='', move='S')
    m.final()
    return m


def ww():
    m = MT('03_reconhecer_ww.jff')
    m.add('inicio', 'abc', 'valida')
    m.add('inicio', [''], 'aceita', move='S')
    m.add('valida', 'abc', 'valida')
    m.add('valida', [''], 'volta', move='L')
    m.add('volta', 'abcABCXYZ', 'volta', move='L')
    m.add('volta', [''], 'divide', move='R')
    m.add('divide', 'ABC', 'divide')
    for a, left, right in zip('abc', 'ABC', 'XYZ'):
        m.add('divide', a, 'fim', write=left)
        m.add('marca_direita', a, 'volta', write=right, move='L')
    m.add('fim', 'abcABCXYZ', 'fim')
    m.add('fim', [''], 'marca_direita', move='L')
    m.add('marca_direita', 'XYZ', 'marca_direita', move='L')
    m.add('divide', 'XYZ', 'volta_compara', move='L')
    m.add('volta_compara', 'ABCXYZLR', 'volta_compara', move='L')
    m.add('volta_compara', [''], 'compara', move='R')
    m.add('compara', 'L', 'compara')
    for left, right in zip('ABC', 'XYZ'):
        state = 'procura_' + right
        m.add('compara', left, state, write='L')
        m.add(state, 'ABCLR', state)
        m.add(state, right, 'volta_compara', write='R', move='L')
    m.add('compara', 'R', 'confere_fim')
    m.add('confere_fim', 'R', 'confere_fim')
    m.add('confere_fim', [''], 'aceita', move='S')
    m.final()
    return m


def maior():
    m = MT('04_primeiro_maior_que_segundo.jff')
    validate_pair(m)
    m.add('prepara', '0', 'prepara', write='Z')
    m.add('prepara', '1', 'ate_separador')
    m.add('prepara', '+', 'zera_direita')
    m.add('ate_separador', '01', 'ate_separador')
    m.add('ate_separador', '+', 'zera_direita')
    m.add('zera_direita', '0', 'zera_direita', write='W')
    m.add('zera_direita', '1', 'retorna_E', move='L')
    m.add('zera_direita', [''], 'retorna_E', move='L')
    for sign in 'EGL':
        back, pick = 'retorna_' + sign, 'escolhe_' + sign
        m.add(back, '01+ZWABXY', back, move='L')
        m.add(back, [''], pick, move='R')
        m.add(pick, 'ZAB', pick)
        for bit, mark in zip('01', 'AB'):
            seek = f'separador_{sign}_{bit}'
            pair = f'par_{sign}_{bit}'
            m.add(pick, bit, seek, write=mark)
            m.add(seek, '01AB', seek)
            m.add(seek, '+', pair)
            m.add(pair, 'WXY', pair)
            for other, marked in zip('01', 'XY'):
                next_sign = sign if sign != 'E' or bit == other else ('G' if bit > other else 'L')
                m.add(pair, other, 'retorna_' + next_sign, write=marked, move='L')
            m.add(pair, [''], 'aceita', move='S')
        end = 'confere_' + sign
        m.add(pick, '+', end)
        m.add(end, 'WXY', end)
        if sign == 'G':
            m.add(end, [''], 'aceita', move='S')
    m.final()
    return m


def test(machines):
    d, s, w, g = machines
    count = 0
    for n in range(256):
        for pad in range(3):
            word = '0' * pad + bin(n)[2:]
            ok, out, _ = d.run(word)
            assert ok and out == word + '0', (word, out)
            count += 1
    for a in range(32):
        for b in range(32):
            for sep in '+#':
                word = bin(a)[2:] + sep + bin(b)[2:]
                ok, out, _ = s.run(word)
                assert ok and int(out, 2) == a + b, (word, out)
                count += 1
    for a in range(32):
        for b in range(32):
            for pad_a, pad_b in [(0, 0), (2, 0), (0, 3), (2, 3)]:
                for sep in '+#':
                    word = '0' * pad_a + bin(a)[2:] + sep + '0' * pad_b + bin(b)[2:]
                    assert g.run(word)[0] == (a > b), word
                    count += 1
    for length in range(9):
        for chars in itertools.product('abc', repeat=length):
            word = ''.join(chars)
            expected = length % 2 == 0 and word[:length//2] == word[length//2:]
            assert w.run(word)[0] == expected, word
            count += 1
    for word, expected in [('acacaacaca', True), ('abacbabacb', True), ('aaabacbbca', False), ('bcbaabcb', False)]:
        assert w.run(word)[0] == expected, word
        count += 1
    for word in ['000+000', '0001+0011', '00101#00011', '11111111+1', '0+11111111']:
        a, b = word.replace('#', '+').split('+')
        ok, out, _ = s.run(word)
        assert ok and int(out, 2) == int(a, 2) + int(b, 2), (word, out)
        count += 1
    for word, expected in [('1010#101', True), ('111#110', True), ('101#101', False), ('10#0001', True), ('0000100#110', False)]:
        assert g.run(word)[0] == expected, word
        count += 1
    for word in ['', '+', '1+', '+1', '1++1', '1#1#1', 'a+1', '1+2', '1 1']:
        assert not s.run(word)[0] and not g.run(word)[0], word
        count += 2
    for word in ['', '2', '10a', '1+1']:
        assert not d.run(word)[0], word
        count += 1
    for word in ['a', 'abc', 'abba', 'abcdabcd', 'AA', 'a a']:
        assert not w.run(word)[0], word
        count += 1
    # Confere a integridade dos arquivos gravados e suas transições.
    for m in machines:
        root = ET.parse(ROOT / m.nome).getroot()
        assert root.findtext('type') == 'turing'
        states = root.findall('automaton/state')
        assert [node.get('name') for node in states] == [f'q{i}' for i in range(len(m.states))]
        assert len(root.findall('automaton/transition')) == len(m.transitions)
    return count


if __name__ == '__main__':
    machines = [dobro(), soma(), ww(), maior()]
    for machine in machines:
        machine.save()
    count = test(machines)
    print(f'OK: {count} verificações; quatro arquivos JFLAP gerados e XML validado.')
    for machine in machines:
        print(f'{machine.nome}: {len(machine.states)} estados, {len(machine.transitions)} transições')
