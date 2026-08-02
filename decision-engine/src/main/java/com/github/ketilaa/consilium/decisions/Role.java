package com.github.ketilaa.consilium.decisions;

/**
 * A named agent role with its mandate text. Equality includes the mandate, so callers
 * should reuse the shared constants in {@link Roles} rather than constructing ad hoc
 * instances with the same name but different wording.
 */
public record Role(String name, String mandate) {

    public Role {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Role name must not be blank");
        }
        if (mandate == null || mandate.isBlank()) {
            throw new IllegalArgumentException("Role mandate must not be blank");
        }
    }

    @Override
    public String toString() {
        return name;
    }
}
