#version 330 core

out vec4 fragColor;

void main()
{
	vec3 color = vec3(0.3764, 0.8509, 0.945);
	fragColor = vec4(color, 1.0);
}