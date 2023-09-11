#pragma once

#include <ogdf/basic/geometry.h>
#include <ogdf/basic/graphics.h>
#include <ogdf/basic/GraphAttributes.h>

namespace ogdf {
	void append(std::initializer_list<double> list, DPolyline &out) {
		for (auto it = list.begin(); it != list.end();) {
			double x = *it, y = *(++it);
			out.emplaceBack(x, y);
			++it;
		}
	};

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


	bool isArrowEnabled(GraphAttributes &m_attr, adjEntry adj) {
		bool result = false;

		if (m_attr.has(GraphAttributes::edgeArrow)) {
			switch (m_attr.arrowType(*adj)) {
				case EdgeArrow::Undefined:
					result = !adj->isSource() && m_attr.directed();
					break;
				case EdgeArrow::First:
					result = adj->isSource();
					break;
				case EdgeArrow::Last:
					result = !adj->isSource();
					break;
				case EdgeArrow::Both:
					result = true;
					break;
				case EdgeArrow::None:;
			}
		} else {
			result = !adj->isSource() && m_attr.directed();
		}

		return result;
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
		return ogdf::isPointCoveredByNode(point, m_attr.point(v), vSize, m_attr.shape(v));
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

			append({end.m_x, y, end.m_x - size / 4, end.m_y, end.m_x + size / 4, end.m_y}, poly);
		} else {
			// identify the position of the tip
			float angle = atan(dy / dx) + (dx < 0 ? Math::pi : 0);
			DPoint head = contourPointFromAngle(angle, m_attr.shape(v),
												DPoint(m_attr.x(v), m_attr.y(v)),
												DPoint(m_attr.width(v), m_attr.height(v)));

			end.m_x = head.m_x;
			end.m_y = head.m_y;

			// draw the actual arrow head

			double length = std::sqrt(dx * dx + dy * dy);
			double dx_norm = dx / length;
			double dy_norm = dy / length;

			double mx = head.m_x - size * dx_norm;
			double my = head.m_y - size * dy_norm;

			double x2 = mx - size / 4 * dy_norm;
			double y2 = my + size / 4 * dx_norm;

			double x3 = mx + size / 4 * dy_norm;
			double y3 = my - size / 4 * dx_norm;

			append({head.m_x, head.m_y, x2, y2, x3, y3}, poly);
		}

		return poly;
	}


	DPolyline drawEdge(edge e, GraphAttributes &m_attr, DPoint *label_pos=nullptr,
					   DPolyline *source_arrow=nullptr, DPolyline *target_arrow=nullptr) {
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
		return points;
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
            auto r = (d * (x - p1)) / d.normSquared();

            if (r < 0) {
                auto l = (x - p1).normSquared();
                if (l < minDist) {
                    minDist = l;
                    out = p1;
                }
            } else if (r > 1) {
                auto l = (x - p2).normSquared();
                if (l < minDist) {
                    minDist = l;
                    out = p2;
                }
            } else {
                auto y = p1 + r * d;
                auto l = (x - y).normSquared();
                if (l < minDist) {
                    minDist = l;
                    out = y;
                }
            }
            p1 = p2;
        }
        return minDist;
    }
};