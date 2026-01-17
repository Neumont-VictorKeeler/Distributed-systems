from typing import Dict, Any
from fastapi import Request


def create_link(request: Request, rel: str, href: str, method: str = "GET") -> Dict[str, Any]:
    """Create a HATEOAS link"""
    base_url = str(request.base_url).rstrip('/')
    return {
        "rel": rel,
        "href": f"{base_url}{href}",
        "method": method
    }


def add_user_links(request: Request, user_id: int, is_owner: bool = False) -> Dict[str, Any]:
    """Add HATEOAS links to user response"""
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
    """Add HATEOAS links to video game response"""
    links = {
        "self": create_link(request, "self", f"/games/{game_id}", "GET"),
        "all_games": create_link(request, "collection", "/games", "GET"),
        "owner": create_link(request, "owner", f"/users/{owner_id}", "GET"),
    }
    
    if is_owner:
        links["update"] = create_link(request, "update", f"/games/{game_id}", "PUT")
        links["delete"] = create_link(request, "delete", f"/games/{game_id}", "DELETE")
    
    return links


def add_collection_links(request: Request, resource_path: str) -> Dict[str, Any]:
    """Add HATEOAS links to collection response"""
    return {
        "self": create_link(request, "self", resource_path, "GET"),
    }


def add_auth_links(request: Request) -> Dict[str, Any]:
    """Add HATEOAS links to authentication response"""
    return {
        "self": create_link(request, "self", "/auth/login", "POST"),
        "register": create_link(request, "register", "/users", "POST"),
        "me": create_link(request, "me", "/users/me", "GET"),
    }

