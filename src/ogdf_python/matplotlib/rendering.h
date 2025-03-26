#pragma once

#include <ogdf/basic/geometry.h>
#include <ogdf/basic/graphics.h>
#include <ogdf/basic/GraphAttributes.h>

namespace ogdf {
	namespace python_matplotlib {
		void append(std::initializer_list<double> list, DPolyline &out) {
			for (auto it = list.begin(); it != list.end();) {
				double x = *it, y = *(++it);
				out.emplaceBack(x, y);
				++it;
			}
		}

		void drawPolygonShape(Shape s, double x, double y, double w, double h, DPolyline &out) {
			// values are precomputed to save expensive sin/cos calls
			const double triangleWidth = 0.43301270189222 * w,
					hexagonHalfHeight = 0.43301270189222 * h,
					pentagonHalfWidth = 0.475528258147577 * w,
					pentagonSmallHeight = 0.154508497187474 * h,
					pentagonSmallWidth = 0.293892626146236 * w,
					pentagonHalfHeight = 0.404508497187474 * h,
					octagonHalfWidth = 0.461939766255643 * w,
					octagonSmallWidth = 0.191341716182545 * w,
					octagonHalfHeight = 0.461939766255643 * h,
					octagonSmallHeight = 0.191341716182545 * h;
			switch (s) {
				case Shape::Triangle:
					append({x, y - h / 2, x + triangleWidth, y + h / 4,
							x - triangleWidth, y + h / 4}, out);
					break;
				case Shape::InvTriangle:
					append({x, y + h / 2, x - triangleWidth, y - h / 4,
							x + triangleWidth, y - h / 4}, out);
					break;
				case Shape::Pentagon:
					append({x, y - h / 2, x + pentagonHalfWidth, y - pentagonSmallHeight,
							x + pentagonSmallWidth, y + pentagonHalfHeight, x - pentagonSmallWidth,
							y + pentagonHalfHeight, x - pentagonHalfWidth, y - pentagonSmallHeight}, out);
					break;
				case Shape::Hexagon:
					append({x + w / 4, y + hexagonHalfHeight, x - w / 4,
							y + hexagonHalfHeight, x - w / 2, y, x - w / 4,
							y - hexagonHalfHeight, x + w / 4, y - hexagonHalfHeight,
							x + w / 2, y}, out);
					break;
				case Shape::Octagon:
					append({x + octagonHalfWidth, y + octagonSmallHeight, x + octagonSmallWidth,
							y + octagonHalfHeight, x - octagonSmallWidth, y + octagonHalfHeight,
							x - octagonHalfWidth, y + octagonSmallHeight, x - octagonHalfWidth,
							y - octagonSmallHeight, x - octagonSmallWidth, y - octagonHalfHeight,
							x + octagonSmallWidth, y - octagonHalfHeight, x + octagonHalfWidth,
							y - octagonSmallHeight}, out);
					break;
				case Shape::Rhomb:
					append({x + w / 2, y, x, y + h / 2, x - w / 2,
							y, x, y - h / 2}, out);
					break;
				case Shape::Trapeze:
					append({x - w / 2, y + h / 2, x + w / 2,
							y + h / 2, x + w / 4, y - h / 2,
							x - w / 4, y - h / 2}, out);
					break;
				case Shape::InvTrapeze:
					append({x - w / 2, y - h / 2, x + w / 2,
							y - h / 2, x + w / 4, y + h / 2,
							x - w / 4, y + h / 2}, out);
					break;
				case Shape::Parallelogram:
					append({x - w / 2, y + h / 2, x + w / 4,
							y + h / 2, x + w / 2, y - h / 2,
							x - w / 4, y - h / 2}, out);
					break;
				case Shape::InvParallelogram:
					append({x - w / 2, y - h / 2, x + w / 4,
							y - h / 2, x + w / 2, y + h / 2,
							x - w / 4, y + h / 2}, out);
					break;
				default:
					OGDF_ASSERT(false); // unsupported shapes are rendered as rectangle
				case Shape::Rect:
					append({x - w / 2, y - h / 2,
							x - w / 2, y + h / 2,
							x + w / 2, y + h / 2,
							x + w / 2, y - h / 2}, out);
					break;
			}
		}

		bool isPointCoveredByNodeOP(const DPoint& point, const DPoint& v, const DPoint& vSize,
				const Shape& shape) {
			const double epsilon = 1e-6;
			const double trapeziumWidthOffset = vSize.m_x * 0.275;
			GenericPolyline<DPoint> polygon;

			auto isInConvexCCWPolygon = [&] {
				for (int i = 0; i < polygon.size(); i++) {
					DPoint edgePt1 = v + *polygon.get(i);
					DPoint edgePt2 = v + *polygon.get((i + 1) % polygon.size());

					if ((edgePt2.m_x - edgePt1.m_x) * (point.m_y - edgePt1.m_y)
									- (edgePt2.m_y - edgePt1.m_y) * (point.m_x - edgePt1.m_x)
							< -epsilon) {
						return false;
					}
				}
				return true;
			};

			auto isInRegularPolygon = [&](unsigned int sides) {
				polygon.clear();
				double radius = (max(vSize.m_x, vSize.m_y) / 2.0);
				for (double angle = -(Math::pi / 2) + Math::pi / sides; angle < 1.5 * Math::pi;
						angle += 2.0 * Math::pi / sides) {
					polygon.pushBack(DPoint(radius * cos(angle), radius * sin(angle)));
				}
				return isInConvexCCWPolygon();
			};

			switch (shape) {
			// currently these tikz polygons are only supported as regular polygons, i.e. width=height
			case Shape::Pentagon:
				return isInRegularPolygon(5);
			case Shape::Hexagon:
				return isInRegularPolygon(6);
			case Shape::Octagon:
				return isInRegularPolygon(8);
			case Shape::Triangle:
				return isInRegularPolygon(3);
			// Non-regular polygons
			case Shape::InvTriangle:
				polygon.pushBack(DPoint(0, -vSize.m_y * 2.0 / 3.0));
				polygon.pushBack(DPoint(vSize.m_x / 2.0, vSize.m_y * 1.0 / 3.0));
				polygon.pushBack(DPoint(-vSize.m_x / 2.0, vSize.m_y * 1.0 / 3.0));
				return isInConvexCCWPolygon();
			case Shape::Rhomb:
				polygon.pushBack(DPoint(vSize.m_x / 2.0, 0));
				polygon.pushBack(DPoint(0, vSize.m_y / 2.0));
				polygon.pushBack(DPoint(-vSize.m_x / 2.0, 0));
				polygon.pushBack(DPoint(0, -vSize.m_y / 2.0));
				return isInConvexCCWPolygon();
			case Shape::Trapeze:
				polygon.pushBack(DPoint(-vSize.m_x / 2.0, -vSize.m_y / 2.0));
				polygon.pushBack(DPoint(vSize.m_x / 2.0, -vSize.m_y / 2.0));
				polygon.pushBack(DPoint(vSize.m_x / 2.0 - trapeziumWidthOffset, +vSize.m_y / 2.0));
				polygon.pushBack(DPoint(-vSize.m_x / 2.0 + trapeziumWidthOffset, +vSize.m_y / 2.0));
				return isInConvexCCWPolygon();
			case Shape::InvTrapeze:
				polygon.pushBack(DPoint(vSize.m_x / 2.0, vSize.m_y / 2.0));
				polygon.pushBack(DPoint(-vSize.m_x / 2.0, vSize.m_y / 2.0));
				polygon.pushBack(DPoint(-vSize.m_x / 2.0 + trapeziumWidthOffset, -vSize.m_y / 2.0));
				polygon.pushBack(DPoint(vSize.m_x / 2.0 - trapeziumWidthOffset, -vSize.m_y / 2.0));
				return isInConvexCCWPolygon();
			case Shape::Parallelogram:
				polygon.pushBack(DPoint(-vSize.m_x / 2.0, -vSize.m_y / 2.0));
				polygon.pushBack(DPoint(vSize.m_x / 2.0 - trapeziumWidthOffset, -vSize.m_y / 2.0));
				polygon.pushBack(DPoint(vSize.m_x / 2.0, +vSize.m_y / 2.0));
				polygon.pushBack(DPoint(-vSize.m_x / 2.0 + trapeziumWidthOffset, +vSize.m_y / 2.0));
				return isInConvexCCWPolygon();
			case Shape::InvParallelogram:
				polygon.pushBack(DPoint(-vSize.m_x / 2.0 + trapeziumWidthOffset, -vSize.m_y / 2.0));
				polygon.pushBack(DPoint(vSize.m_x / 2.0, -vSize.m_y / 2.0));
				polygon.pushBack(DPoint(vSize.m_x / 2.0 - trapeziumWidthOffset, vSize.m_y / 2.0));
				polygon.pushBack(DPoint(-vSize.m_x / 2.0, vSize.m_y / 2.0));
				return isInConvexCCWPolygon();
			// Ellipse
			case Shape::Ellipse:
				return pow((point.m_x - v.m_x) / (vSize.m_x * 0.5), 2)
						+ pow((point.m_y - v.m_y) / (vSize.m_y * 0.5), 2)
						< 1;
			// Simple x y comparison
			case Shape::Rect:
			case Shape::RoundedRect:
			default:
				return point.m_x + epsilon >= v.m_x - vSize.m_x / 2.0
						&& point.m_x - epsilon <= v.m_x + vSize.m_x / 2.0
						&& point.m_y + epsilon >= v.m_y - vSize.m_y / 2.0
						&& point.m_y - epsilon <= v.m_y + vSize.m_y / 2.0;
			}
		}

		DPoint contourPointFromAngleOP(double angle, int n, double rotationOffset, const DPoint& center,
				const DPoint& vSize) {
			// math visualised: https://www.desmos.com/calculator/j6iktd7fs4
			double nOffset = floor((angle - rotationOffset) / (2 * Math::pi / n)) * 2 * Math::pi / n;
			double polyLineStartAngle = rotationOffset + nOffset;
			double polyLineEndAngle = polyLineStartAngle + 2 * Math::pi / n;
			DLine polyLine = DLine(-cos(polyLineStartAngle), -sin(polyLineStartAngle),
					-cos(polyLineEndAngle), -sin(polyLineEndAngle));

			DLine originLine = DLine(0, 0, cos(angle), sin(angle));

			DPoint intersectionPoint;
			originLine.intersection(polyLine, intersectionPoint);
			intersectionPoint = DPoint(intersectionPoint.m_x * vSize.m_x, intersectionPoint.m_y * vSize.m_y);
			return intersectionPoint + center;
		}

		DPoint contourPointFromAngleOP(double angle, Shape shape, const DPoint& center, const DPoint& vSize) {
			angle = std::fmod(angle, 2 * Math::pi);
			if (angle < 0) {
				angle += Math::pi * 2;
			}

			switch (shape) {
			case Shape::Triangle:
				return contourPointFromAngleOP(angle, 3, Math::pi / 2, center, vSize * .5);
			case Shape::InvTriangle:
				return center - contourPointFromAngleOP(angle + Math::pi, Shape::Triangle, DPoint(), vSize);
			case Shape::Image:
			case Shape::RoundedRect:
			case Shape::Rect:
				return contourPointFromAngleOP(angle, 4, Math::pi / 4, center, vSize / sqrt(2));
			case Shape::Pentagon:
				return contourPointFromAngleOP(angle, 5, Math::pi / 2, center, vSize / 2);
			case Shape::Hexagon:
				return contourPointFromAngleOP(angle, 6, 0, center, vSize / 2);
			case Shape::Octagon:
				return contourPointFromAngleOP(angle, 8, Math::pi / 8, center, vSize / 2);
			case Shape::Rhomb:
				return contourPointFromAngleOP(angle, 4, Math::pi / 2, center, vSize / 2);
			case Shape::Trapeze:
				if (angle < atan(2) || angle >= Math::pi * 7 / 4) {
					DPoint other = contourPointFromAngleOP(Math::pi - angle, Shape::Trapeze, DPoint(), vSize);
					other.m_x *= -1;
					return other + center;
				} else if (angle < Math::pi - atan(2)) {
					return contourPointFromAngleOP(angle, Shape::Rect, center, vSize);
				} else if (angle < Math::pi * 5 / 4) {
					DLine tLine = DLine(.5, -1, 1, 1);
					DLine eLine = DLine(0, 0, 2 * cos(angle), 2 * sin(angle));
					DPoint iPoint;
					tLine.intersection(eLine, iPoint);
					iPoint = DPoint(iPoint.m_x * vSize.m_x * .5, iPoint.m_y * vSize.m_y * .5);
					return iPoint + center;
				} else { // angle < Math::pi * 7 / 4
					return contourPointFromAngleOP(angle, Shape::Rect, center, vSize);
				}
			case Shape::InvTrapeze:
				return center - contourPointFromAngleOP(angle + Math::pi, Shape::Trapeze, DPoint(), vSize);
			case Shape::Parallelogram:
				if (angle < atan(2) || angle > Math::pi * 7 / 4) {
					DLine tLine = DLine(-.5, -1, -1, 1);
					DLine eLine = DLine(0, 0, 2 * cos(angle), 2 * sin(angle));
					DPoint iPoint;
					tLine.intersection(eLine, iPoint);
					iPoint = DPoint(iPoint.m_x * vSize.m_x * .5, iPoint.m_y * vSize.m_y * .5);
					return iPoint + center;
				} else if (angle < Math::pi * 3 / 4) {
					return contourPointFromAngleOP(angle, Shape::Rect, center, vSize);
				} else if (angle < Math::pi + atan(2)) {
					DLine tLine = DLine(.5, 1, 1, -1);
					DLine eLine = DLine(0, 0, 2 * cos(angle), 2 * sin(angle));
					DPoint iPoint;
					tLine.intersection(eLine, iPoint);
					iPoint = DPoint(iPoint.m_x * vSize.m_x * .5, iPoint.m_y * vSize.m_y * .5);
					return iPoint + center;
				} else { // angle < Math::pi * 7 / 4
					return contourPointFromAngleOP(angle, Shape::Rect, center, vSize);
				}
			case Shape::InvParallelogram: {
				DPoint p = contourPointFromAngleOP(Math::pi - angle, Shape::Parallelogram, DPoint(), vSize);
				p.m_x *= -1;
				return p + center;
			}
			case Shape::Ellipse:
			default:
				return DPoint(-vSize.m_x * .5 * cos(angle), -vSize.m_y * .5 * sin(angle)) + center;
			}
		}

		bool isArrowEnabled(GraphAttributes &m_attr, adjEntry adj) {
		    if (m_attr.has(GraphAttributes::edgeArrow)) {
				switch (m_attr.arrowType(*adj)) {
					case EdgeArrow::Undefined:
						return !adj->isSource() && m_attr.directed();
					case EdgeArrow::First:
						return adj->isSource();
					case EdgeArrow::Last:
						return !adj->isSource();
					case EdgeArrow::Both:
						return true;
					case EdgeArrow::None:
					default:
					    return false;
				}
			} else {
				return !adj->isSource() && m_attr.directed();
			}
		}

		double getArrowSize(GraphAttributes &m_attr, adjEntry adj) {
			double result = 0;

			if (isArrowEnabled(m_attr, adj)) {
				const double minSize =
						(m_attr.has(GraphAttributes::edgeStyle) ? m_attr.strokeWidth(adj->theEdge()) : 1) * 3;
				node v = adj->theNode();
				node w = adj->twinNode();
				result = std::max(minSize,
								  (m_attr.width(v) + m_attr.height(v) + m_attr.width(w) + m_attr.height(w)) / 16.0);
			}

			return result;
		}

		bool isCoveredBy(GraphAttributes &m_attr, const DPoint &point, adjEntry adj) {
			node v = adj->theNode();
			DPoint vSize = DPoint(m_attr.width(v), m_attr.height(v));
			return isPointCoveredByNodeOP(point, m_attr.point(v), vSize, m_attr.shape(v));
		}

		DPolyline drawArrowHead(const DPoint &start, DPoint &end, adjEntry adj, GraphAttributes &m_attr) {
			const double dx = end.m_x - start.m_x;
			const double dy = end.m_y - start.m_y;
			const double size = getArrowSize(m_attr, adj);
			node v = adj->theNode();
		
			DPolyline poly;
			if (dx == 0) {
				int sign = dy > 0 ? 1 : -1;
				double y = m_attr.y(v) - m_attr.height(v) / 2 * sign;
				end.m_y = y - sign * size;
		
				append({end.m_x, y, end.m_x - size / 4, y - size * sign,
				        end.m_x + size / 4, y - size * sign, end.m_x, y}, poly);
			} else {
				// identify the position of the tip
				double slope = dy / dx;
				int sign = dx > 0 ? 1 : -1;
		
				double x = m_attr.x(v) - m_attr.width(v) / 2 * sign;
				double delta = x - start.m_x;
				double y = start.m_y + delta * slope;
		
				if (!isCoveredBy(m_attr, DPoint(x, y), adj)) {
					sign = dy > 0 ? 1 : -1;
					y = m_attr.y(v) - m_attr.height(v) / 2 * sign;
					delta = y - start.m_y;
					x = start.m_x + delta / slope;
				}
		
				end.m_x = x;
				end.m_y = y;
		
				// draw the actual arrow head
		
				double dx2 = end.m_x - start.m_x;
				double dy2 = end.m_y - start.m_y;
				double length = std::sqrt(dx2 * dx2 + dy2 * dy2);
				dx2 /= length;
				dy2 /= length;
		
				double mx = end.m_x - size * dx2;
				double my = end.m_y - size * dy2;
		
				double x2 = mx - size / 4 * dy2;
				double y2 = my + size / 4 * dx2;
		
				double x3 = mx + size / 4 * dy2;
				double y3 = my - size / 4 * dx2;
		
				append({end.m_x, end.m_y, x2, y2, x3, y3, end.m_x, end.m_y}, poly);
			}

			return poly;
		}


		DPolyline drawEdge(edge e, GraphAttributes &m_attr, DPoint *label_pos = nullptr,
						   DPolyline *source_arrow = nullptr, DPolyline *target_arrow = nullptr) {
			bool drawSourceArrow = isArrowEnabled(m_attr, e->adjSource());
			bool drawTargetArrow = isArrowEnabled(m_attr, e->adjTarget());
			bool drawLabel = m_attr.has(GraphAttributes::edgeLabel) && !m_attr.label(e).empty();

			DPolyline path = m_attr.bends(e);
			node s = e->source();
			node t = e->target();
			path.pushFront(m_attr.point(s));
			path.pushBack(m_attr.point(t));

			bool drawSegment = false;
			bool finished = false;

			DPolyline points;
			for (ListConstIterator<DPoint> it = path.begin(); it.succ().valid() && !finished; it++) {
				DPoint p1 = *it;
				DPoint p2 = *(it.succ());

				// leaving segment at source node ?
				if (isCoveredBy(m_attr, p1, e->adjSource()) && !isCoveredBy(m_attr, p2, e->adjSource())) {
					if (!drawSegment && drawSourceArrow && source_arrow) {
						*source_arrow = drawArrowHead(p2, p1, e->adjSource(), m_attr);
					}

					drawSegment = true;
				}

				// entering segment at target node ?
				if (!isCoveredBy(m_attr, p1, e->adjTarget()) && isCoveredBy(m_attr, p2, e->adjTarget())) {
					finished = true;

					if (drawTargetArrow && target_arrow) {
						*target_arrow = drawArrowHead(p1, p2, e->adjTarget(), m_attr);
					}
				}

				if (drawSegment && drawLabel && label_pos) {
					label_pos->m_x = (p1.m_x + p2.m_x) / 2;
					label_pos->m_y = (p1.m_y + p2.m_y) / 2;

					drawLabel = false;
				}

				if (drawSegment) {
					points.pushBack(p1);
				}

				if (finished) {
					points.pushBack(p2);
				}
			}
			if (points.size() < 2) {
				return path;
			}
			return points;
		}

		template<class PointType>
		DRect getBoundingBox(const GenericPolyline<PointType> &poly) {
			DPoint p1{std::numeric_limits<double>::min(), std::numeric_limits<double>::min()};
			DPoint p2{std::numeric_limits<double>::max(), std::numeric_limits<double>::max()};
			for (auto p: poly) {
				Math::updateMin(p1.m_x, p.m_x);
				Math::updateMax(p2.m_x, p.m_x);
				Math::updateMin(p1.m_y, p.m_y);
				Math::updateMax(p2.m_y, p.m_y);
			}
			return DRect{p1, p2};
		}

		double normSquared(const DPoint &p) {
			return p.m_x * p.m_x + p.m_y * p.m_y;
		}

		double closestPointOnLine(const DPolyline &line, const DPoint &x, DPoint &out) {
			if (line.size() == 0) {
				return std::numeric_limits<double>::quiet_NaN();
			} else if (line.size() == 1) {
				out = line.front();
				return out.distance(x);
			}
			auto it = line.begin();
			auto p1 = *it;
			it++;
			double minDist = std::numeric_limits<double>::infinity();
			for (auto p2 = *it; it != line.end(); it++) {
				// https://stackoverflow.com/a/10984080/805569
				p2 = *it;
				auto d = p2 - p1;
				auto r = (d * (x - p1)) / normSquared(d);

				if (r < 0) {
					auto l = normSquared(x - p1);
					if (l < minDist) {
						minDist = l;
						out = p1;
					}
				} else if (r > 1) {
					auto l = normSquared(x - p2);
					if (l < minDist) {
						minDist = l;
						out = p2;
					}
				} else {
					auto y = p1 + r * d;
					auto l = normSquared(x - y);
					if (l < minDist) {
						minDist = l;
						out = y;
					}
				}
				p1 = p2;
			}
			return minDist;
		}

		double closestPointOnEdge(const GraphAttributes &GA, edge e, const DPoint &x, DPoint &out) {
			DPoint p1 = GA.point(e->source()), p2;
			double minDist = std::numeric_limits<double>::infinity();
			auto handle = [&](const DPoint &n) {
				// https://stackoverflow.com/a/10984080/805569
				p2 = n;
				auto d = p2 - p1;
				auto r = (d * (x - p1)) / normSquared(d);

				if (r < 0) {
					auto l = normSquared(x - p1);
					if (l < minDist) {
						minDist = l;
						out = p1;
					}
				} else if (r > 1) {
					auto l = normSquared(x - p2);
					if (l < minDist) {
						minDist = l;
						out = p2;
					}
				} else {
					auto y = p1 + r * d;
					auto l = normSquared(x - y);
					if (l < minDist) {
						minDist = l;
						out = y;
					}
				}
				p1 = p2;
			};
			for (auto n: GA.bends(e)) {
				handle(n);
			}
			handle(GA.point(e->target()));
			return minDist;
		}

		edge findClosestEdge(const GraphAttributes &GA, const DPoint &x, DPoint &out) {
			DPoint cur;
			edge res = nullptr;
			double minDist = std::numeric_limits<double>::infinity();
			for (edge e: GA.constGraph().edges) {
				double d = closestPointOnEdge(GA, e, x, cur);
				if (d < minDist) {
					res = e;
					minDist = d;
					out = cur;
				}
			}
			return res;
		}

		node findClosestNode(const GraphAttributes &GA, const DPoint &x) {
			node res = nullptr;
			double minDist = std::numeric_limits<double>::infinity();
			for (node n: GA.constGraph().nodes) {
				double d = normSquared(x - GA.point(n));
				if (d < minDist) {
					res = n;
					minDist = d;
				}
			}
			return res;
		}
	}
}
