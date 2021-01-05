#version 330 core
layout(location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

vec3 UnprojectPoint(float x, float y, float z) {
    vec4 unprojectedPoint =  inverse(model) * inverse(view) * inverse(proj) * vec4(x, y, z, 1.0);
    return unprojectedPoint.xyz / unprojectedPoint.w;
}

out vec3 nearPoint;
out vec3 farPoint;

void main()
{
    vec3 p = aPos;
    nearPoint = UnprojectPoint(p.x, p.y, 0);
    farPoint = UnprojectPoint(p.x, p.y, 1);
    gl_Position = vec4(aPos, 1.0);
}