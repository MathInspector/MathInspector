#version 330 core
layout(location = 0) in vec3 vPos;
layout(location = 1) in vec2 aFragCoord;
layout(location = 2) in vec3 aNormal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec2 fragCoord;
out vec3 normal;
out vec4 fragPos;

void main()
{
	fragCoord = aFragCoord;
	normal = aNormal;
	fragPos = model * vec4(vPos, 1.0);
	gl_Position = projection * view * fragPos;
}