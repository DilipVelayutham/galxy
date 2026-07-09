const http = require("http");
const url = require("url");

// Seed data
let products = [];
let reviews = [];
let testimonials = [];

const sendJSON = (res, statusCode, success, message, data) => {
  res.writeHead(statusCode, {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "http://localhost:3000",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization"
  });
  res.end(JSON.stringify({ success, message, data }));
};

const handleCorsPreflight = (req, res) => {
  res.writeHead(204, {
    "Access-Control-Allow-Origin": "http://localhost:3000",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization"
  });
  res.end();
};

const server = http.createServer((req, res) => {
  if (req.method === "OPTIONS") {
    handleCorsPreflight(req, res);
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const query = parsedUrl.query;

  // Helpers to read body
  const readBody = (callback) => {
    let body = "";
    req.on("data", chunk => { body += chunk; });
    req.on("end", () => {
      try {
        callback(JSON.parse(body || "{}"));
      } catch (e) {
        callback({});
      }
    });
  };

  // Routing
  if (path === "/api/products" && req.method === "GET") {
    sendJSON(res, 200, true, "Products list loaded", products);
    return;
  }

  if (path === "/api/admin/reviews" && req.method === "GET") {
    const page = parseInt(query.page || "1", 10);
    const limit = parseInt(query.limit || "10", 10);
    const isApproved = query.is_approved === "true";
    const productId = query.product_id;
    const search = query.search ? query.search.trim().toLowerCase() : "";

    let filtered = reviews.filter(r => r.is_approved === isApproved);

    if (productId) {
      filtered = filtered.filter(r => r.product_id === productId);
    }

    if (search) {
      filtered = filtered.filter(r => 
        (r.customer_name && r.customer_name.toLowerCase().includes(search)) ||
        (r.comment && r.comment.toLowerCase().includes(search)) ||
        (r.title && r.title.toLowerCase().includes(search)) ||
        (r.order_number && r.order_number.toLowerCase().includes(search)) ||
        (r.product_name && r.product_name.toLowerCase().includes(search))
      );
    }

    const total = filtered.length;
    const total_pages = Math.max(1, Math.ceil(total / limit));
    const start = (page - 1) * limit;
    const items = filtered.slice(start, start + limit);

    sendJSON(res, 200, true, "Reviews queue loaded", {
      reviews: items,
      total,
      page,
      limit,
      total_pages
    });
    return;
  }

  if (path === "/api/admin/reviews" && req.method === "POST") {
    readBody((body) => {
      const _id = "r_" + Math.random().toString(36).substr(2, 9);
      const product = products.find(p => p._id === body.product_id) || null;
      const newReview = {
        _id,
        product_id: body.product_id || "",
        product,
        product_name: body.product_name || (product ? product.name : ""),
        customer_name: body.customer_name || "Anonymous",
        email: body.email || "",
        title: body.title || "",
        rating: parseInt(body.rating || "5", 10),
        comment: body.comment || "",
        order_number: body.order_number || "",
        is_approved: false,
        is_featured: !!body.is_featured,
        images: body.images || [],
        status: "pending",
        created_at: new Date().toISOString(),
        submitted_at: new Date().toISOString()
      };
      reviews.push(newReview);
      sendJSON(res, 201, true, "Review created", newReview);
    });
    return;
  }

  // approve review
  if (path.startsWith("/api/admin/reviews/") && path.endsWith("/approve") && req.method === "PUT") {
    const parts = path.split("/");
    const id = parts[4];
    const review = reviews.find(r => r._id === id);
    if (review) {
      review.is_approved = true;
      review.status = "approved";
      sendJSON(res, 200, true, "Review approved", review);
    } else {
      sendJSON(res, 404, false, "Review not found", null);
    }
    return;
  }

  // reject review
  if (path.startsWith("/api/admin/reviews/") && path.endsWith("/reject") && req.method === "PUT") {
    const parts = path.split("/");
    const id = parts[4];
    const review = reviews.find(r => r._id === id);
    if (review) {
      readBody((body) => {
        review.is_approved = false;
        review.status = "rejected";
        review.rejection_reason = body.reason || "";
        sendJSON(res, 200, true, "Review rejected", review);
      });
    } else {
      sendJSON(res, 404, false, "Review not found", null);
    }
    return;
  }

  // promote to testimonial
  if (path.startsWith("/api/admin/reviews/") && path.endsWith("/promote-to-testimonial") && req.method === "POST") {
    const parts = path.split("/");
    const id = parts[4];
    const review = reviews.find(r => r._id === id);
    if (review) {
      readBody((body) => {
        const _id = "t_" + Math.random().toString(36).substr(2, 9);
        const newTestimonial = {
          _id,
          customer_name: review.customer_name,
          customer_location: body.customer_location || "",
          quote: review.comment,
          rating: review.rating,
          image_url: review.images[0] || "",
          source: "review",
          display_order: parseInt(body.display_order || "1", 10),
          is_active: true,
          created_at: new Date().toISOString()
        };
        testimonials.push(newTestimonial);
        sendJSON(res, 200, true, "Review promoted to testimonial", newTestimonial);
      });
    } else {
      sendJSON(res, 404, false, "Review not found", null);
    }
    return;
  }

  // update review
  if (path.startsWith("/api/admin/reviews/") && req.method === "PUT") {
    const parts = path.split("/");
    const id = parts[4];
    const review = reviews.find(r => r._id === id);
    if (review) {
      readBody((body) => {
        Object.assign(review, body);
        sendJSON(res, 200, true, "Review updated", review);
      });
    } else {
      sendJSON(res, 404, false, "Review not found", null);
    }
    return;
  }

  // delete review
  if (path.startsWith("/api/admin/reviews/") && req.method === "DELETE") {
    const parts = path.split("/");
    const id = parts[4];
    const index = reviews.findIndex(r => r._id === id);
    if (index !== -1) {
      reviews.splice(index, 1);
      sendJSON(res, 200, true, "Review deleted", null);
    } else {
      sendJSON(res, 404, false, "Review not found", null);
    }
    return;
  }

  // testimonials list
  if (path === "/api/admin/testimonials" && req.method === "GET") {
    sendJSON(res, 200, true, "Testimonials queue loaded", {
      testimonials,
      total: testimonials.length
    });
    return;
  }

  // create testimonial
  if (path === "/api/admin/testimonials" && req.method === "POST") {
    readBody((body) => {
      const _id = "t_" + Math.random().toString(36).substr(2, 9);
      const newTestimonial = {
        _id,
        customer_name: body.customer_name || "Anonymous",
        customer_location: body.customer_location || "",
        quote: body.quote || "",
        rating: parseInt(body.rating || "5", 10),
        image_url: body.image_url || "",
        source: "manual",
        display_order: testimonials.length + 1,
        is_active: body.is_active !== false,
        created_at: new Date().toISOString()
      };
      testimonials.push(newTestimonial);
      sendJSON(res, 201, true, "Testimonial created", newTestimonial);
    });
    return;
  }

  // update testimonial
  if (path.startsWith("/api/admin/testimonials/") && req.method === "PUT") {
    const parts = path.split("/");
    const id = parts[4];
    const testimonial = testimonials.find(t => t._id === id);
    if (testimonial) {
      readBody((body) => {
        Object.assign(testimonial, body);
        sendJSON(res, 200, true, "Testimonial updated", testimonial);
      });
    } else {
      sendJSON(res, 404, false, "Testimonial not found", null);
    }
    return;
  }

  // delete testimonial
  if (path.startsWith("/api/admin/testimonials/") && req.method === "DELETE") {
    const parts = path.split("/");
    const id = parts[4];
    const index = testimonials.findIndex(t => t._id === id);
    if (index !== -1) {
      testimonials.splice(index, 1);
      sendJSON(res, 200, true, "Testimonial deleted", null);
    } else {
      sendJSON(res, 404, false, "Testimonial not found", null);
    }
    return;
  }

  // reorder testimonials
  if (path === "/api/admin/testimonials/reorder" && req.method === "PUT") {
    readBody((body) => {
      if (Array.isArray(body)) {
        body.forEach(item => {
          const t = testimonials.find(x => x._id === item.testimonial_id);
          if (t) {
            t.display_order = item.display_order;
          }
        });
        testimonials.sort((a, b) => a.display_order - b.display_order);
        sendJSON(res, 200, true, "Testimonials reordered", testimonials);
      } else {
        sendJSON(res, 400, false, "Invalid payload format", null);
      }
    });
    return;
  }

  sendJSON(res, 404, false, "Not Found", null);
});

const PORT = 5000;
server.listen(PORT, () => {
  console.log(`[MOCK API] Mock API server running at http://localhost:${PORT}`);
});
