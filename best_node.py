# -*- encoding: utf-8 -*-

from bs4 import BeautifulSoup

def calculate_best_node(html):

    soup = BeautifulSoup(html)
    top_node = None
    nodes = nodes_to_check(soup)

    starting_boost = float(1.0)
    cnt = 0
    i = 0
    parent_nodes = []
    nodes_with_text = []

    for node in nodes:
        text = node.get_text()
        high_link_density = is_highlink_density(node)
        if len(text) > 5 and not high_link_density:
            nodes_with_text.append(node)

    nodes_number = len(nodes_with_text)
    negative_scoring = 0
    bottom_negativescore_nodes = float(nodes_number) * 0.25

    for node in nodes_with_text:
        boost_score = float(0)

        if is_boostable(node):
            if cnt >= 0:
                boost_score = float((1.0 / starting_boost) * 50)
                starting_boost += 1

        if nodes_number > 15:
            if (nodes_number - i) <= bottom_negativescore_nodes:
                booster = float(bottom_negativescore_nodes - (nodes_number - i))
                boost_score = float(-pow(booster, float(2)))
                negscore = abs(boost_score) + negative_scoring
                if negscore > 40: 
                    boost_score = float(5)
        text_node = node.get_text()
        upscore = int(len(text_node) + boost_score)

        parent_node = node.parent

        update_score(parent_node, upscore)
        update_node_count(parent_node, 1)

        if parent_node not in parent_nodes:
            parent_nodes.append(parent_node)
        
        parent_parent_node = parent_node.parent
        if parent_parent_node is not None:
            update_score(parent_parent_node, upscore / 2)
            update_node_count(parent_parent_node, 1)
            if parent_parent_node not in parent_nodes:
                parent_nodes.append(parent_parent_node)
        cnt += 1
        i += 1

    top_node_score = 0
    for e in parent_nodes:
        score = get_score(e)
        if top_node_score < score:
            top_node_score = score
            top_node = e

        if top_node is None:
            top_node = e
    return top_node

def get_score(node):
    return node.gravity_score if node.gravity_score else 0

def update_node_count(node, add_to_count):
    current_node_count = 0
    if node.gravity_nodes:
        current_node_count = node.gravity_nodes
    current_node_count += add_to_count

    node.gravity_nodes = current_node_count


def update_score(node, upscore):
    current_score = 0
    if node.gravity_score:
        current_score = node.gravity_score

    new_score = current_score + upscore
    node.gravity_score = new_score

def nodes_to_check(e):
    nodes = []
    for tag in ['td', 'pre', 'p']:
        etags = e.find_all(tag)
        if etags:
            nodes += etags
    return nodes

def is_highlink_density(e):
    links = e.find_all('a')
    if not links:
        return False
    word_len = len(e.get_text())
    if word_len == 0:
        return True
    sb = []
    for link in links:
        sb.append(link.get_text())
    link_text = ''.join(sb)
    number_of_link_words = len(link_text)
    number_of_links = len(links)
    link_divisor = number_of_link_words / float(word_len)
    score = link_divisor * number_of_links
    if score >= 1.0:
        return True
    return False

def is_boostable(node):
    para = u'p'
    steps_away = 0
    min_word_count = 10
    max_steps_away_from_node = 3
    nodes = walk_siblings(node)

    for current_node in nodes:
        current_node_tag = current_node.name
        if current_node_tag == para:
            if steps_away > max_steps_away_from_node:
                return False
            para_text = current_node.get_text()
            if len(para_text) > max_steps_away_from_node:
                return True
            steps_away += 1

    return False

def walk_siblings(node):
    current_sibling = node.previous_sibling
    nodes = []
    while current_sibling is not None:
        nodes.append(current_sibling)
        previous_sibling = current_sibling.previous_sibling
        current_sibling = None if previous_sibling is None else previous_sibling

    return nodes

if __name__ == '__main__':
    import requests
    res = requests.request('get', '')
    print calculate_best_node(res.text).get_text()
