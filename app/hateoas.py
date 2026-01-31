from typing import Dict, Any
from fastapi import Request


def create_link(request: Request, rel: str, href: str, method: str = "GET") -> Dict[str, Any]:
    base_url = str(request.base_url).rstrip('/')
    return {
        "rel": rel,
        "href": f"{base_url}{href}",
        "method": method
    }


def add_user_links(request: Request, user_id: int, is_owner: bool = False) -> Dict[str, Any]:
    links = {
        "self": create_link(request, "self", f"/users/{user_id}", "GET"),
        "all_users": create_link(request, "collection", "/users", "GET"),
    }

    if is_owner:
        links["update"] = create_link(request, "update", f"/users/{user_id}", "PUT")
        links["games"] = create_link(request, "games", f"/users/{user_id}/games", "GET")
        links["create_game"] = create_link(request, "create_game", "/games", "POST")

    return links


def add_game_links(request: Request, game_id: int, owner_id: int, is_owner: bool = False) -> Dict[str, Any]:
    links = {
        "self": create_link(request, "self", f"/games/{game_id}", "GET"),
        "all_games": create_link(request, "collection", "/games", "GET"),
        "owner": create_link(request, "owner", f"/users/{owner_id}", "GET"),
    }

    if is_owner:
        links["update"] = create_link(request, "update", f"/games/{game_id}", "PUT")
        links["delete"] = create_link(request, "delete", f"/games/{game_id}", "DELETE")

    return links


def add_collection_links(request: Request, resource_path: str, skip: int = 0, limit: int = 100, count: int = 0) -> Dict[str, Any]:
    links = {
        "self": create_link(request, "self", resource_path, "GET"),
    }

    if skip > 0:
        prev_skip = max(0, skip - limit)
        links["prev"] = create_link(request, "prev", f"{resource_path}?skip={prev_skip}&limit={limit}", "GET")

    if count == limit:
        next_skip = skip + limit
        links["next"] = create_link(request, "next", f"{resource_path}?skip={next_skip}&limit={limit}", "GET")

    return links


def add_auth_links(request: Request) -> Dict[str, Any]:
    return {
        "self": create_link(request, "self", "/auth/login", "POST"),
        "register": create_link(request, "register", "/users", "POST"),
        "me": create_link(request, "me", "/users/me", "GET"),
    }


def add_trade_offer_links(request: Request, trade_offer_id: int, offerer_id: int, receiver_id: int) -> Dict[str, Any]:
    links = {
        "self": create_link(request, "self", f"/trade-offers/{trade_offer_id}", "GET"),
        "all_trade_offers": create_link(request, "collection", "/trade-offers", "GET"),
        "offerer": create_link(request, "offerer", f"/users/{offerer_id}", "GET"),
        "receiver": create_link(request, "receiver", f"/users/{receiver_id}", "GET"),
        "accept": create_link(request, "accept", f"/trade-offers/{trade_offer_id}/accept", "PUT"),
        "reject": create_link(request, "reject", f"/trade-offers/{trade_offer_id}/reject", "PUT"),
        "cancel": create_link(request, "cancel", f"/trade-offers/{trade_offer_id}/cancel", "PUT"),
    }

    return links

